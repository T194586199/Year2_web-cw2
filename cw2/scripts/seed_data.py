"""
Data seeding script
Run: python scripts/seed_data.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Ensure we can import the app package from project root
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app, db
from app.models import User, Post, Tag, Comment
from sqlalchemy import text

def seed_data(clear_existing=False):
    """
    Seed data
    
    Args:
        clear_existing: If True, will clear existing data first
    """
    app = create_app()
    with app.app_context():
        if clear_existing:
            print("Warning: Will clear existing data...")
            confirm = input("Confirm clearing existing data? (Enter 'yes' to confirm, any other key to skip): ")
            if confirm.lower() == 'yes':
                # Clear all data
                Comment.query.delete()
                db.session.execute(text("DELETE FROM post_tags"))
                db.session.execute(text("DELETE FROM post_likes"))
                db.session.execute(text("DELETE FROM comment_likes"))
                db.session.execute(text("DELETE FROM bookmarks"))
                db.session.execute(text("DELETE FROM follows"))
                Post.query.delete()
                Tag.query.delete()
                User.query.delete()
                db.session.commit()
                print("Existing data cleared\n")
            else:
                print("Skipping clear, continuing to add data...\n")
        
        print("Starting data seeding...")
        
        # 1. Create users (15)
        users = []
        for i in range(15):
            user = User(
                username=f'user{i+1}',
                email=f'user{i+1}@example.com',
                bio=f'Badminton enthusiast {i+1}, love sports!'
            )
            user.set_password('password123')
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        print(f"Created {len(users)} users")
        
        # 2. Create tags (40)
        tag_names = [
            'Singles Technique', 'Doubles Coordination', 'Serving', 'Receiving', 'Net Play',
            'Backcourt', 'Footwork', 'Fitness', 'Tactics', 'Match Experience',
            'Racket Recommendation', 'Shoe Selection', 'String Selection', 'Grip Recommendation', 'Equipment Review',
            'Lin Dan', 'Lee Chong Wei', 'Axelsen', 'Momota', 'Shi Yuqi',
            'Olympics', 'World Championships', 'All England', 'China Open', 'Japan Open',
            'Backhand', 'Forehand', 'Smash', 'Drop Shot', 'Drive',
            'Mixed Doubles', 'Men\'s Doubles', 'Women\'s Doubles', 'Men\'s Singles', 'Women\'s Singles',
            'Beginner', 'Advanced', 'Professional Training', 'Amateur Competition', 'Club Activities'
        ]
        tags = []
        for name in tag_names:
            tag = Tag(name=name, description=f'Discussion about {name}')
            tags.append(tag)
            db.session.add(tag)
        
        db.session.commit()
        print(f"Created {len(tags)} tags")
        
        # 3. Create posts (80)
        categories = ['Technique', 'Equipment', 'Tournament', 'Training', 'Other']
        post_titles = [
            'How to improve backhand technique?', 'Recommend a racket for beginners', '2024 All England Open Review',
            'Key points of doubles coordination', 'Serving tips', 'How to choose strings?', 'Footwork training methods',
            'Lin Dan classic match review', 'Mixed doubles tactics analysis', 'Net play technique explained'
        ]
        
        posts = []
        for i in range(80):
            author = random.choice(users)
            title = f"{random.choice(post_titles)} - {i+1}"
            content = f"This is the content of post {i+1}. Here you can write about badminton, such as technical points, equipment recommendations, match analysis, etc.\n\n" * 3
            post = Post(
                title=title,
                content=content,
                author=author,
                category=random.choice(categories),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                view_count=random.randint(0, 1000),
                like_count=random.randint(0, 100),
                comment_count=random.randint(0, 50)
            )
            
            # Randomly assign tags (1-5)
            post_tags = random.sample(tags, random.randint(1, min(5, len(tags))))
            post.tags = post_tags
            for tag in post_tags:
                tag.increment_usage()
            
            posts.append(post)
            db.session.add(post)
        
        db.session.commit()
        print(f"Created {len(posts)} posts")
        
        # 4. Create comments (200)
        for i in range(200):
            post = random.choice(posts)
            author = random.choice(users)
            comment = Comment(
                post=post,
                author=author,
                content=f'This is comment {i+1}, very insightful!',
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 20))
            )
            post.comment_count += 1
            db.session.add(comment)
        
        db.session.commit()
        print(f"Created 200 comments")
        
        # 5. Create follow relationships
        for user in users:
            # Each user randomly follows 3-8 other users
            following = random.sample([u for u in users if u != user], 
                                     random.randint(3, min(8, len(users)-1)))
            for follow_user in following:
                user.follow(follow_user)
        
        db.session.commit()
        print("Created follow relationships")
        
        # 6. Create bookmark relationships
        for user in users:
            # Each user randomly bookmarks 5-15 posts
            bookmarked = random.sample(posts, random.randint(5, min(15, len(posts))))
            user.bookmarked_posts = bookmarked
        
        db.session.commit()
        print("Created bookmark relationships")
        
        # 7. Create like relationships
        for user in users:
            # Each user randomly likes 10-30 posts
            liked = random.sample(posts, random.randint(10, min(30, len(posts))))
            user.liked_posts = liked
            for post in liked:
                post.like_count += 1
        
        db.session.commit()
        print("Created like relationships")
        
        print("\nData seeding completed!")
        print(f"Users: {User.query.count()}")
        print(f"Posts: {Post.query.count()}")
        print(f"Tags: {Tag.query.count()}")
        print(f"Comments: {Comment.query.count()}")

if __name__ == '__main__':
    seed_data()


