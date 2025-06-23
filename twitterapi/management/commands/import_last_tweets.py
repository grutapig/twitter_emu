import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from twitterapi.models import User, Tweet


class Command(BaseCommand):
    help = 'Import last tweets from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            default='docs/last_tweets.csv',
            help='Path to CSV file (default: docs/last_tweets.csv)'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        if not os.path.exists(csv_file):
            self.stdout.write(
                self.style.ERROR(f'CSV file not found: {csv_file}')
            )
            return

        self.stdout.write(f'Starting import from {csv_file}')
        
        # Read and parse CSV
        tweets_data = []
        skipped_no_user = 0
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row_num, row in enumerate(reader, start=2):  # Start at 2 since CSV has header
                self.stdout.write(f'Processing row {row_num}: author_id={row["author_id"]}, tweet_id={row["tweet_id"]}')
                
                # Find user by twitter_id (author_id in CSV)
                try:
                    user = User.objects.get(twitter_id=row['author_id'])
                    self.stdout.write(f'  ✓ Found user: @{user.screen_name} (twitter_id: {user.twitter_id})')
                    
                    tweets_data.append({
                        'user': user,
                        'author_name': row['author_name'],
                        'author_id': row['author_id'], 
                        'tweet_id': row['tweet_id'],
                        'text': row['text'],
                        'created_at': row['created_at'],
                        'reply_count': int(row['reply_count']) if row['reply_count'] else 0,
                        'row_num': row_num
                    })
                    
                except User.DoesNotExist:
                    self.stdout.write(f'  ✗ User not found for author_id: {row["author_id"]} (author_name: {row["author_name"]})')
                    skipped_no_user += 1
                    continue
                except Exception as e:
                    self.stdout.write(f'  ✗ Error processing row {row_num}: {str(e)}')
                    continue

        self.stdout.write('=' * 50)
        self.stdout.write(f'Found {len(tweets_data)} tweets to import')
        self.stdout.write(f'Skipped {skipped_no_user} tweets (user not found)')

        if not tweets_data:
            self.stdout.write(self.style.WARNING('No tweets to import'))
            return

        # Import tweets
        imported_count = 0
        skipped_exists = 0
        failed_count = 0
        
        with transaction.atomic():
            for tweet_data in tweets_data:
                self.stdout.write(f'Importing tweet {tweet_data["tweet_id"]} by @{tweet_data["user"].screen_name}...')
                
                # Check if tweet already exists
                if Tweet.objects.filter(twitter_id=tweet_data['tweet_id']).exists():
                    self.stdout.write(f'  ✗ Tweet {tweet_data["tweet_id"]} already exists, skipping')
                    skipped_exists += 1
                    continue
                
                try:
                    # Parse date - format: "Sun Jun 15 19:44:06 +0000 2025" 
                    try:
                        created_at = datetime.strptime(tweet_data['created_at'], '%a %b %d %H:%M:%S %z %Y')
                        self.stdout.write(f'  ✓ Parsed date: {created_at}')
                    except ValueError as e:
                        self.stdout.write(f'  ✗ Date parse error for "{tweet_data["created_at"]}": {str(e)}')
                        created_at = datetime.now()
                        self.stdout.write(f'  ⚠ Using current time instead: {created_at}')

                    # Create tweet
                    tweet = Tweet.objects.create(
                        twitter_id=tweet_data['tweet_id'],
                        text=tweet_data['text'],
                        author=tweet_data['user'],
                        community=None,  # These are user tweets, not community tweets
                        reply_to=None,   # Not handling replies in this import
                        created_at=created_at
                    )
                    
                    self.stdout.write(f'  ✓ Created tweet: {tweet.twitter_id} - "{tweet.text[:50]}..."')
                    imported_count += 1
                    
                except Exception as e:
                    self.stdout.write(f'  ✗ Error creating tweet {tweet_data["tweet_id"]}: {str(e)}')
                    failed_count += 1
                    continue

        # Final summary
        self.stdout.write('=' * 50) 
        self.stdout.write(self.style.SUCCESS('IMPORT SUMMARY:'))
        self.stdout.write(f'  Successfully imported: {imported_count} tweets')
        self.stdout.write(f'  Skipped (already exists): {skipped_exists} tweets')
        self.stdout.write(f'  Skipped (user not found): {skipped_no_user} tweets')
        self.stdout.write(f'  Failed to import: {failed_count} tweets')
        self.stdout.write(f'  Total processed: {len(tweets_data) + skipped_no_user} rows')
        
        if imported_count > 0:
            self.stdout.write(self.style.SUCCESS('Import completed successfully!'))
        else:
            self.stdout.write(self.style.WARNING('No new tweets were imported'))