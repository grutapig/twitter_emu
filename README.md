# Twitter API Emulator

A Django-based Twitter API emulation platform designed for debugging, monitoring, and analyzing Twitter-like communities and user interactions.

## 🎯 Purpose

This project serves as a **testing and development tool** for applications that integrate with Twitter API. It provides a controlled environment to:

- **Debug** Twitter API integrations without hitting rate limits
- **Troubleshoot** social media monitoring applications
- **Analyze** community interactions and user behaviors
- **Monitor** tweet patterns and conversation threads
- **Test** data processing pipelines with realistic social media data

## 🌟 Key Features

### API Emulation
- **Twitter-Compatible Endpoints**: Mimics popular Twitter API endpoints for seamless integration testing
- **Cursor-Based Pagination**: Implements Twitter-style pagination for realistic data flow
- **Community Support**: Advanced community tweet management for group discussions
- **Thread Management**: Full reply/conversation threading with proper hierarchy

### User Interface
- **Vue.js Frontend**: Modern web interface for data visualization and interaction
- **Community Views**: Browse and analyze community discussions
- **User Profiles**: Detailed user timelines and follower/following relationships
- **Tweet Threads**: Navigate conversation chains and reply structures

### Data Management
- **Admin Panel**: Full Django admin interface for deep data control
- **Flexible Tweet Creation**: Create tweets, replies, and community posts from any user
- **CSV Import**: Bulk import existing Twitter data for testing scenarios
- **Rich User Models**: Twitter-style user profiles with social graph relationships

### Developer Tools
- **RESTful API**: Clean JSON API for programmatic access
- **Test Suite**: Comprehensive test coverage for all endpoints
- **Fixtures**: Pre-loaded crypto community data for immediate testing
- **Documentation**: Well-documented codebase with examples

## 🏗️ Architecture

### Django Apps Structure
- **`twitterapi`**: Core Twitter emulation (Users, Communities, Tweets, REST API)
- **`api`**: Additional API endpoints for data management
- **`ui_vue`**: Vue.js frontend interface (prepared for future development)

### Database Schema
- **Custom User Model**: Extended AbstractUser with Twitter-specific fields
- **Community Model**: Groups for organizing themed discussions
- **Tweet Model**: Full-featured tweets with replies, threading, and community support
- **Social Graph**: Many-to-many follower/following relationships

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 5.2.3
- Django REST Framework 3.16.0

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd twitter_emu
   ```

2. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -m requirements.txt
   ```

4. **Setup database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Load sample data**
   ```bash
   python manage.py loaddata crypto_fixture.json
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

## 📚 API Documentation

### Twitter-Style Endpoints (`/twitter/`)

#### Community Tweets
```http
GET /twitter/community/tweets/?community_id=<twitter_id>
```
Retrieve paginated tweets from a specific community.

#### User Timeline
```http
GET /twitter/user/last_tweets/?userId=<twitter_id>&include_replies=<boolean>
GET /twitter/user/last_tweets/?userName=<screen_name>&include_replies=<boolean>
```
Get user's recent tweets with optional reply inclusion.

#### Tweet Replies
```http
GET /twitter/tweet/replies/?tweetId=<twitter_id>
```
Fetch all replies to a specific tweet.

#### User Relationships
```http
GET /twitter/user/followers/?userName=<screen_name>
GET /twitter/user/followings/?userName=<screen_name>
```
Retrieve user's followers and following lists.

### Management API (`/api/`)

#### Communities
```http
GET /api/communities/                    # List all communities
GET /api/communities/<id>/              # Community details with tweets
```

#### Users
```http
GET /api/users/search/?q=<query>        # Search users
GET /api/users/<id>/                    # User profile and tweets
```

#### Tweets
```http
GET /api/tweets/<id>/                   # Tweet details with replies
GET /api/tweets/<id>/replies/           # Tweet replies only
POST /api/tweets/create/                # Create new tweet
DELETE /api/tweets/<id>/delete/         # Delete tweet and replies
```

### Request/Response Examples

**Create Tweet:**
```json
POST /api/tweets/create/
{
  "text": "Hello Twitter API Emulator! 🚀",
  "author_id": 1,
  "community_id": 1,
  "reply_to_id": null
}
```

**Response:**
```json
{
  "tweet": {
    "id": 123,
    "twitter_id": "1234567890123456789",
    "text": "Hello Twitter API Emulator! 🚀",
    "author": {
      "id": 1,
      "screen_name": "test_user",
      "name": "Test User"
    },
    "created_at": "2024-12-23T15:30:00Z",
    "reply_count": 0
  }
}
```

## 🗄️ Data Management

### Sample Data
The project includes realistic crypto community data:
- **DogeSquad**: Dog-themed crypto community
- **KittyCoin**: Cat-themed crypto community
- **10 Users**: Various personalities (optimists, pessimists, founders, analysts)
- **90 Tweets**: Complete conversation threads with realistic crypto discussions

### Import Custom Data
```bash
python manage.py import_community_tweets <csv_file_path>
```

### Admin Interface
Access the admin panel at `/admin/` for:
- User management with Twitter-specific fields
- Community creation and management
- Tweet creation, editing, and threading
- Advanced search and filtering capabilities

## 🧪 Testing

### Run All Tests
```bash
python manage.py test
```

### Test Specific Components
```bash
# Twitter API endpoints
python manage.py test twitterapi.tests.TwitterAPIEndpointsTest

# Management API endpoints
python manage.py test api.tests.APIEndpointsTest
```

### Test Coverage
- **GET Endpoints**: All read operations with pagination
- **POST Endpoints**: Tweet creation with validation
- **DELETE Endpoints**: Tweet deletion with cascade
- **Error Handling**: 400, 404 status codes
- **Edge Cases**: Empty data, invalid IDs, missing parameters

## 🛠️ Development

### Project Structure
```
twitter_emu/
├── twitterapi/          # Core Twitter API emulation
│   ├── models.py        # User, Community, Tweet models
│   ├── views.py         # DRF API views
│   ├── serializers.py   # JSON serialization
│   ├── pagination.py    # Twitter-style pagination
│   └── fixtures/        # Sample data
├── api/                 # Management API
│   ├── views.py         # CRUD operations
│   └── urls.py          # API routing
├── ui_vue/              # Frontend interface
└── docs/                # Sample data and documentation
```

### Adding New Features
1. **Models**: Extend existing models or create new ones in `twitterapi/models.py`
2. **API**: Add new endpoints in `twitterapi/views.py` or `api/views.py`
3. **Tests**: Create corresponding test cases following the existing pattern
4. **Fixtures**: Update sample data as needed

### Key Components
- **Custom User Model**: Twitter-compatible user system
- **Auto-Generated IDs**: 19-character Twitter-style IDs
- **Social Graph**: Asymmetric follower relationships
- **Community System**: Organized group discussions
- **Thread Management**: Full conversation hierarchy

## 🚨 Important Notes

### Development Use Only
- **NOT for Production**: This is an MVP/testing tool
- **Security**: Default Django secret key included (change for any deployment)
- **Database**: SQLite for development (configure PostgreSQL for production)
- **Rate Limiting**: Not implemented (add if needed for testing scenarios)

### Limitations
- **Authentication**: Basic Django auth (implement OAuth for Twitter compatibility)
- **Real-time**: No WebSocket support (polling-based updates)
- **Media**: Text-only tweets (extend for images/videos)
- **Verification**: No blue checkmarks or verification system

## 🤝 Contributing

This project is designed for debugging and testing purposes. Feel free to:
- Add new API endpoints that match Twitter's behavior
- Implement additional social media features
- Improve test coverage
- Add frontend components for better visualization
- Create more realistic sample datasets

## 📄 License

This project is intended for development and testing purposes. Please respect Twitter's terms of service when using this tool to develop applications that interact with their platform.

---

**Happy Testing! 🐦✨**