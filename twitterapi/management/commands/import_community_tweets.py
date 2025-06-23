import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from twitterapi.models import User, Community, Tweet


class Command(BaseCommand):
    help = 'Import community tweets from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            default='docs/community_tweets.csv',
            help='Path to CSV file (default: docs/community_tweets.csv)'
        )
        parser.add_argument(
            '--community-name',
            type=str,
            default='Dark',
            help='Community name to import tweets to (default: Dark)'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        community_name = options['community_name']
        
        if not os.path.exists(csv_file):
            self.stdout.write(
                self.style.ERROR(f'CSV file not found: {csv_file}')
            )
            return

        self.stdout.write(f'Starting import from {csv_file}')
        
        with transaction.atomic():
            # Create or get community
            community, created = Community.objects.get_or_create(
                name=community_name
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created community: {community_name}')
                )
            else:
                self.stdout.write(f'Using existing community: {community_name}')

            # Read and parse CSV
            tweets_data = []
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    tweets_data.append({
                        'author_username': row['автор_сообщения'],
                        'tweet_id': row['id_твита'],
                        'author_id': row['id_автора'],
                        'date': row['дата_сообщения'],
                        'reply_count': int(row['количество_ответов']) if row['количество_ответов'] else 0,
                        'reply_to_id': row['ответ_на_твит'] if row['ответ_на_твит'] else None,
                        'text': row['текст_сообщения'],
                    })

            self.stdout.write(f'Found {len(tweets_data)} tweets to import')

            # Step 1: Import tweets without relations (original posts)
            self.stdout.write('Step 1: Importing tweets without relations...')
            imported_count = 0
            for tweet_data in tweets_data:
                if not tweet_data['reply_to_id']:  # No reply relation
                    if self._import_tweet(tweet_data, community, None):
                        imported_count += 1
            
            self.stdout.write(f'Imported {imported_count} original tweets')

            # Step 2: Import tweets with relations to already imported tweets
            self.stdout.write('Step 2: Importing tweets with existing relations...')
            imported_count = 0
            for tweet_data in tweets_data:
                if tweet_data['reply_to_id']:  # Has reply relation
                    if Tweet.objects.filter(twitter_id=tweet_data['reply_to_id']).exists():
                        if self._import_tweet(tweet_data, community, tweet_data['reply_to_id']):
                            imported_count += 1
            
            self.stdout.write(f'Imported {imported_count} reply tweets with existing parents')

            # Step 3: Import remaining tweets (replies to not-yet-imported tweets)
            self.stdout.write('Step 3: Importing remaining tweets...')
            imported_count = 0
            remaining_tweets = []
            
            for tweet_data in tweets_data:
                if tweet_data['reply_to_id'] and not Tweet.objects.filter(twitter_id=tweet_data['tweet_id']).exists():
                    remaining_tweets.append(tweet_data)
            
            # Keep trying to import remaining tweets until no more can be imported
            max_iterations = 10
            iteration = 0
            while remaining_tweets and iteration < max_iterations:
                iteration += 1
                self.stdout.write(f'  Iteration {iteration}: {len(remaining_tweets)} tweets remaining')
                
                imported_this_round = 0
                tweets_to_remove = []
                
                for i, tweet_data in enumerate(remaining_tweets):
                    # Check if parent tweet now exists
                    if Tweet.objects.filter(twitter_id=tweet_data['reply_to_id']).exists():
                        if self._import_tweet(tweet_data, community, tweet_data['reply_to_id']):
                            imported_this_round += 1
                            imported_count += 1
                            tweets_to_remove.append(i)
                
                # Remove imported tweets from remaining list
                for i in reversed(tweets_to_remove):
                    remaining_tweets.pop(i)
                
                if imported_this_round == 0:
                    break
            
            self.stdout.write(f'Imported {imported_count} remaining tweets')
            
            if remaining_tweets:
                self.stdout.write(
                    self.style.WARNING(f'{len(remaining_tweets)} tweets could not be imported (missing parent tweets)')
                )

        self.stdout.write(
            self.style.SUCCESS('Import completed successfully!')
        )

    def _import_tweet(self, tweet_data, community, reply_to_id):
        """Import a single tweet, return True if successful"""
        try:
            # Skip if tweet already exists
            if Tweet.objects.filter(twitter_id=tweet_data['tweet_id']).exists():
                return False

            # Create or get user
            user, created = User.objects.get_or_create(
                screen_name=tweet_data['author_username'],
                defaults={
                    'username': tweet_data['author_username'],
                    'name': tweet_data['author_username'],
                    'twitter_id': tweet_data['author_id']
                }
            )
            
            # If user exists but doesn't have twitter_id, update it
            if not created and not user.twitter_id:
                user.twitter_id = tweet_data['author_id']
                user.save()

            # Parse date
            try:
                # Parse date format: "Sat Jun 14 14:33:06 +0000 2025"
                created_at = datetime.strptime(tweet_data['date'], '%a %b %d %H:%M:%S %z %Y')
            except ValueError:
                print(tweet_data['date'])
                created_at = datetime.now()

            # Get reply_to tweet if specified
            reply_to_tweet = None
            if reply_to_id:
                try:
                    reply_to_tweet = Tweet.objects.get(twitter_id=reply_to_id)
                except Tweet.DoesNotExist:
                    return False  # Parent tweet doesn't exist yet

            # Determine if this should be a community post or regular tweet
            # If it's not a reply, it's a community post
            tweet_community = community if not reply_to_id else None

            # Create tweet
            Tweet.objects.create(
                twitter_id=tweet_data['tweet_id'],
                text=tweet_data['text'],
                author=user,
                community=tweet_community,
                reply_to=reply_to_tweet,
                created_at=created_at,
                updated_at=created_at
            )
            
            return True

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing tweet {tweet_data["tweet_id"]}: {str(e)}')
            )
            return False