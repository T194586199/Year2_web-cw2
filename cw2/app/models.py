from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# Many-to-many relationship intermediate tables
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False)
)

follows = db.Table('follows',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('following_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False),
    db.UniqueConstraint('follower_id', 'following_id', name='unique_follow')
)

bookmarks = db.Table('bookmarks',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False),
    db.UniqueConstraint('user_id', 'post_id', name='unique_bookmark')
)

post_likes = db.Table('post_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False),
    db.UniqueConstraint('user_id', 'post_id', name='unique_post_like')
)

comment_likes = db.Table('comment_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comments.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False),
    db.UniqueConstraint('user_id', 'comment_id', name='unique_comment_like')
)


class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(255), default='default_avatar.png')
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # 关系
    posts = db.relationship('Post', backref='author', lazy='dynamic', 
                           cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic',
                              cascade='all, delete-orphan')
    
    following = db.relationship(
        'User', secondary=follows,
        primaryjoin=('follows.c.follower_id == User.id'),
        secondaryjoin=('follows.c.following_id == User.id'),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )
    bookmarked_posts = db.relationship(
        'Post', secondary=bookmarks,
        backref=db.backref('bookmarked_by', lazy='dynamic'),
        lazy='dynamic'
    )
    liked_posts = db.relationship(
        'Post', secondary=post_likes,
        backref=db.backref('liked_by', lazy='dynamic'),
        lazy='dynamic'
    )
    liked_comments = db.relationship(
        'Comment', secondary=comment_likes,
        backref=db.backref('liked_by', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def set_password(self, password):
        """Set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def is_following(self, user):
        """Check if following a user"""
        return self.following.filter(
            follows.c.following_id == user.id
        ).count() > 0
    
    def follow(self, user):
        """Follow user"""
        if not self.is_following(user) and user != self:
            self.following.append(user)
            return True
        return False
    
    def unfollow(self, user):
        """Unfollow user"""
        if self.is_following(user):
            self.following.remove(user)
            return True
        return False
    
    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    """帖子模型"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category = db.Column(db.String(20), nullable=False, index=True, default='Other')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                         onupdate=datetime.utcnow, nullable=False)
    view_count = db.Column(db.Integer, default=0, nullable=False)
    like_count = db.Column(db.Integer, default=0, nullable=False)
    comment_count = db.Column(db.Integer, default=0, nullable=False)
    is_pinned = db.Column(db.Boolean, default=False, nullable=False)
    is_draft = db.Column(db.Boolean, default=False, nullable=False)
    
    # 关系
    comments = db.relationship('Comment', backref='post', lazy='dynamic',
                              cascade='all, delete-orphan', order_by='Comment.created_at')
    tags = db.relationship(
        'Tag', secondary=post_tags,
        backref=db.backref('posts', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def increment_view(self):
        """Increment view count"""
        self.view_count += 1
        db.session.commit()
    
    def calculate_hot_score(self):
        """Calculate hotness score"""
        hours_old = (datetime.utcnow() - self.created_at).total_seconds() / 3600
        time_factor = max(0, 1 - hours_old / 168)  # Time decay within a week
        return (self.like_count * 2 + 
                self.comment_count * 3 + 
                self.view_count * 0.1) * (1 + time_factor)
    
    def __repr__(self):
        return f'<Post {self.title}>'


class Tag(db.Model):
    """标签模型"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    usage_count = db.Column(db.Integer, default=0, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def increment_usage(self):
        """Increment usage count"""
        if self.usage_count is None:
            self.usage_count = 0
        self.usage_count += 1
    
    def decrement_usage(self):
        """Decrement usage count"""
        if self.usage_count is None:
            self.usage_count = 0
        if self.usage_count > 0:
            self.usage_count -= 1
    
    def __repr__(self):
        return f'<Tag {self.name}>'


class Comment(db.Model):
    """评论模型"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                          onupdate=datetime.utcnow, nullable=True)
    like_count = db.Column(db.Integer, default=0, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]),
                            lazy='dynamic', cascade='all, delete-orphan')
    
    def get_depth(self):
        """Calculate comment depth"""
        depth = 0
        parent = self.parent
        while parent and depth < 3:
            depth += 1
            parent = parent.parent
        return depth
    
    def __repr__(self):
        return f'<Comment {self.id}>'


