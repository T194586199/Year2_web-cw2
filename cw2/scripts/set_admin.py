"""
Script to set a user as admin
Usage: python scripts/set_admin.py <username>
"""

import sys
from pathlib import Path

# Ensure we can import the app package from project root
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app, db
from app.models import User

def set_admin(username):
    """Set a user as admin"""
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"Error: User '{username}' not found.")
            print("\nAvailable users:")
            users = User.query.order_by(User.username).all()
            if users:
                for u in users:
                    admin_status = " (admin)" if u.is_admin else ""
                    print(f"  - {u.username}{admin_status}")
            else:
                print("  No users found in database.")
            return False
        
        if user.is_admin:
            print(f"User '{username}' is already an admin.")
            return True
        
        user.is_admin = True
        db.session.commit()
        print(f"Successfully set '{username}' as admin.")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/set_admin.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    set_admin(username)

