"""
Script to list all users in the database
Usage: python scripts/list_users.py
"""

import sys
from pathlib import Path

# Ensure we can import the app package from project root
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app, db
from app.models import User

def list_users():
    """List all users"""
    app = create_app()
    with app.app_context():
        users = User.query.order_by(User.username).all()
        
        if not users:
            print("No users found in the database.")
            return
        
        print(f"\nTotal users: {len(users)}\n")
        print(f"{'Username':<20} {'Email':<30} {'Admin':<8} {'Active':<8} {'Posts':<8} {'Comments':<8}")
        print("-" * 90)
        
        for user in users:
            admin_status = "Yes" if user.is_admin else "No"
            active_status = "Yes" if user.is_active else "No"
            posts_count = user.posts.count()
            comments_count = user.comments.filter_by(is_deleted=False).count()
            
            print(f"{user.username:<20} {user.email:<30} {admin_status:<8} {active_status:<8} {posts_count:<8} {comments_count:<8}")
        
        print("\n")

if __name__ == '__main__':
    list_users()

