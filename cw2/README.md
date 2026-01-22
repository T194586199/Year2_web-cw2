# Badminton Online Forum

A modern, feature-rich web forum application for badminton enthusiasts built with Flask. Share knowledge, discuss techniques, equipment, tournaments, and training tips with the community.

**Note**: This is a local development/testing application. Follow the instructions below to set it up and run it on your computer.

## Features

### Core Functionality
- **User Authentication & Profiles**: Secure registration, login, and user profile management with avatar uploads
- **Post Management**: Create, edit, and delete posts with Markdown support and code syntax highlighting
- **Rich Content**: Full Markdown support including code blocks, tables, and formatting
- **Tag System**: Organize posts with tags and browse by tag
- **Commenting System**: Threaded comments with up to 3 levels of nesting
- **Social Interactions**: Like posts and comments, bookmark posts for later reading
- **Real-time Search**: Instant search suggestions as you type, with support for tags and post titles
- **Recommendation System**: Personalized post recommendations based on user interests and behavior
- **Category Filtering**: Organize content by categories (Technique, Equipment, Tournament, Training, Other)
- **Responsive Design**: Modern, mobile-friendly interface with glassmorphism effects

### Advanced Features
- **Intelligent Recommendations**: Algorithm considers user likes, bookmarks, published posts, and tag interests
- **Hot Posts**: Trending posts based on engagement metrics (likes, comments, time)
- **Draft System**: Save posts as drafts before publishing
- **Admin Panel**: Comprehensive admin dashboard for managing posts, users, comments, and tags
- **Accessibility**: WCAG 2.1 compliant with keyboard navigation, ARIA labels, and skip links
- **AJAX Interactions**: Seamless like/bookmark actions without page reload

## Technology Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF, WTForms
- **Migrations**: Flask-Migrate
- **Content Processing**: Python-Markdown, Pygments (syntax highlighting)
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Security**: Werkzeug password hashing, CSRF protection

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cw2
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional)
   
   For local testing, environment variables are optional. The application will use default values if not set. If you want to customize, create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///instance/database.db
   FLASK_ENV=development
   ```
   
   To generate a SECRET_KEY for testing:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **Initialize the database**
   ```bash
   flask db upgrade
   ```

6. **Apply admin migration** (if upgrading from older version)
   ```bash
   flask db upgrade
   ```
   This will add the `is_admin` field to the users table.

7. **Seed sample data** (optional)
   ```bash
   python scripts/seed_data.py
   ```

8. **Set up admin user** (optional)
   ```bash
   python scripts/set_admin.py <username>
   ```
   Replace `<username>` with the username you want to make an admin.

## Running the Application

To run the application locally on your computer:

```bash
python run.py
```

The application will start in development mode and be available at `http://localhost:5000`

Open your web browser and navigate to `http://localhost:5000` to access the forum.

**Note**: This is for local testing only. The application uses Flask's built-in development server, which is suitable for local development and testing.

## Project Structure

```
cw2/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration settings
│   ├── models.py            # Database models (User, Post, Tag, Comment)
│   ├── routes.py            # Application routes and views
│   ├── forms.py             # WTForms form definitions
│   └── utils.py             # Utility functions (Markdown, recommendations)
├── templates/               # Jinja2 templates
│   ├── base.html           # Base template
│   ├── index.html          # Homepage
│   ├── post_create.html    # Post creation/editing
│   ├── post_detail.html    # Post detail view
│   ├── user_profile.html   # User profile
│   └── ...                 # Other templates
├── static/
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── images/             # Images and uploads
├── migrations/             # Database migrations
├── instance/               # Instance folder (database, config)
├── scripts/                # Utility scripts
│   ├── seed_data.py       # Seed sample data
│   └── clear_data.py      # Clear database
├── requirements.txt        # Python dependencies
└── run.py                 # Application entry point
```

## Configuration

Key configuration options in `app/config.py` (for local testing):

- `SECRET_KEY`: Secret key for session management (optional for local testing)
- `SQLALCHEMY_DATABASE_URI`: Database connection string (defaults to SQLite in `instance/database.db`)
- `POSTS_PER_PAGE`: Number of posts per page (default: 20)
- `MAX_CONTENT_LENGTH`: Maximum file upload size (default: 5MB)
- `UPLOAD_FOLDER`: Directory for uploaded images
- `MARKDOWN_EXTENSIONS`: Markdown processing extensions

The application will work with default settings for local testing. No configuration changes are required.

## Database Migrations

Create a new migration:
```bash
flask db migrate -m "Description of changes"
```

Apply migrations:
```bash
flask db upgrade
```

Revert last migration:
```bash
flask db downgrade
```

## Key Routes

- `/` - Homepage with posts, categories, and recommendations
- `/auth/register` - User registration
- `/auth/login` - User login
- `/post/create` - Create new post
- `/post/<id>` - View post details
- `/tag/<name>` - View posts by tag
- `/user/<username>` - User profile
- `/settings` - User settings
- `/search?q=...` - Search posts and tags
- `/admin` - Admin dashboard (admin only)
- `/admin/posts` - Manage posts (admin only)
- `/admin/users` - Manage users (admin only)
- `/admin/comments` - Manage comments (admin only)
- `/admin/tags` - Manage tags (admin only)
- `/api/search/suggest` - AJAX search suggestions endpoint
- `/api/post/<id>/like` - AJAX like/unlike endpoint
- `/api/post/<id>/bookmark` - AJAX bookmark/unbookmark endpoint

## Features in Detail

### Recommendation Algorithm
The recommendation system calculates personalized scores based on:
- Tag interest weights (40%): Based on user's liked posts, bookmarks, and published posts
- User similarity (30%): Similar users based on shared interests
- Hotness score (20%): Post engagement metrics
- Time factor (10%): Recency of the post

### Real-time Search
- 300ms debounce to prevent excessive requests
- Searches both tags and post titles simultaneously
- Keyboard navigation support (arrow keys, Enter, Escape)
- Returns up to 10 suggestions

### Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation throughout
- ARIA labels and roles
- Skip links for screen readers
- High contrast ratios for text

## Development

### Flask Shell Context
Access database models easily:
```bash
flask shell
>>> User.query.all()
>>> Post.query.filter_by(is_draft=False).all()
```

### Clearing Data
To clear all data (use with caution):
```bash
python scripts/clear_data.py
```

## Admin Features

The application includes a comprehensive admin panel for managing the forum. Admin features include:

### Admin Dashboard
- View statistics: total users, posts, comments, tags
- View recent posts and users
- Quick access to all management sections

### Post Management
- View all posts with search and category filtering
- Delete any post
- Pin/unpin posts to the top
- View post statistics (views, likes, comments)

### User Management
- View all users with search functionality
- Activate/deactivate user accounts
- Grant/revoke admin privileges
- View user statistics (posts, comments)

### Comment Management
- View all comments with search functionality
- Delete any comment
- View comment statistics

### Tag Management
- View all tags with usage counts
- Delete unused tags
- Search tags

### Setting Up Admin

To set a user as admin, use the provided script:
```bash
python scripts/set_admin.py <username>
```

Or manually in Flask shell:
```bash
flask shell
>>> from app.models import User
>>> user = User.query.filter_by(username='your_username').first()
>>> user.is_admin = True
>>> db.session.commit()
```

**Note**: Only users with `is_admin=True` can access the admin panel. The admin link appears in the navigation bar for admin users only.

