from datetime import datetime, timedelta
from app.models import Post, User, Tag
from app import db
from flask import url_for

# Category mapping - maps both English and Chinese category names to display names
CATEGORY_MAP = {
    # English categories
    'Technique': 'Technique',
    'Equipment': 'Equipment',
    'Tournament': 'Tournament',
    'Training': 'Training',
    'Other': 'Other',
    # Chinese categories (for backward compatibility)
    '技术': 'Technique',
    '装备': 'Equipment',
    '比赛': 'Tournament',
    '训练': 'Training',
    '其他': 'Other',
}

def get_category_display(category):
    """Get display name for category, converting Chinese to English if needed"""
    if not category:
        return 'Other'
    return CATEGORY_MAP.get(category, category)

def render_markdown(text):
    """Render Markdown to HTML"""
    import markdown
    from flask import current_app
    
    # Get extensions from config, or use default extension list
    extensions = current_app.config.get(
        'MARKDOWN_EXTENSIONS',
        ['codehilite', 'fenced_code', 'tables', 'nl2br']
    )
    md = markdown.Markdown(extensions=extensions)
    html = md.convert(text or '')
    return html


def get_text_preview(text, max_length=100):
    """
    Extract plain text preview from Markdown text
    Remove Markdown syntax, return plain text
    """
    import re
    
    if not text:
        return ''
    
    # Remove Markdown links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove Markdown images !![alt](url) -> alt
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)
    
    # Remove bold **text** -> text
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    
    # Remove italic *text* -> text
    text = re.sub(r'(?<!\*)\*([^\*]+)\*(?!\*)', r'\1', text)
    
    # Remove inline code `code` -> code
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove heading markers # text -> text
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    # Remove list markers - text or * text -> text
    text = re.sub(r'^[\-\*\+]\s+', '', text, flags=re.MULTILINE)
    
    # Remove extra blank lines
    text = re.sub(r'\n\s*\n', '\n', text)
    
    # Strip leading and trailing whitespace
    text = text.strip()
    
    # Truncate to specified length
    if len(text) > max_length:
        text = text[:max_length] + '...'
    
    return text


def get_avatar_url(user):
    """Get user avatar URL"""
    from flask import url_for
    if user.avatar_url and user.avatar_url != 'default_avatar.png':
        return url_for('static', filename=f'images/uploads/{user.avatar_url}')
    else:
        return url_for('static', filename='images/default_avatar.png')


def time_ago(dt):
    """Calculate relative time"""
    if not dt:
        return ''
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff < timedelta(minutes=1):
        return 'just now'
    elif diff < timedelta(hours=1):
        return f'{int(diff.seconds / 60)} minutes ago'
    elif diff < timedelta(days=1):
        return f'{int(diff.seconds / 3600)} hours ago'
    elif diff < timedelta(days=30):
        return f'{diff.days} days ago'
    else:
        return dt.strftime('%Y-%m-%d')


def get_hot_posts(limit=15):
    """获取热门帖子"""
    posts = Post.query.filter_by(is_draft=False).all()
    scored_posts = [(post, post.calculate_hot_score()) for post in posts]
    scored_posts.sort(key=lambda x: x[1], reverse=True)
    # 去重（按ID）
    seen_ids = set()
    unique_posts = []
    for post, score in scored_posts:
        if post.id not in seen_ids:
            seen_ids.add(post.id)
            unique_posts.append(post)
        if len(unique_posts) >= limit:
            break
    return unique_posts


def analyze_user_tags(user):
    """Analyze user's interest weights for tags"""
    tag_weights = {}
    
    # Liked posts (weight 3)
    for post in user.liked_posts:
        for tag in post.tags:
            tag_weights[tag.id] = tag_weights.get(tag.id, 0) + 3
    
    # Bookmarked posts (weight 2)
    for post in user.bookmarked_posts:
        for tag in post.tags:
            tag_weights[tag.id] = tag_weights.get(tag.id, 0) + 2
    
    # Published posts (weight 1)
    for post in user.posts:
        for tag in post.tags:
            tag_weights[tag.id] = tag_weights.get(tag.id, 0) + 1
    
    return tag_weights


def find_similar_users(user, limit=10):
    """Find similar users"""
    similar_users = {}
    
    # Based on follow relationships
    for following in user.following:
        for follower in following.followers:
            if follower.id != user.id:
                similar_users[follower.id] = similar_users.get(follower.id, 0) + 1
    
    # Based on liking same posts
    user_liked_posts = {post.id for post in user.liked_posts}
    for post in Post.query.all():
        if post.id in user_liked_posts:
            for liker in post.liked_by:
                if liker.id != user.id:
                    similar_users[liker.id] = similar_users.get(liker.id, 0) + 1
    
    # 排序并返回用户对象
    sorted_users = sorted(similar_users.items(), key=lambda x: x[1], reverse=True)
    user_ids = [uid for uid, score in sorted_users[:limit]]
    return User.query.filter(User.id.in_(user_ids)).all()


def calculate_recommendation_score(post, user, user_tags, similar_users):
    """Calculate recommendation score"""
    # Tag matching (40%)
    tag_score = 0
    for tag in post.tags:
        tag_score += user_tags.get(tag.id, 0)
    tag_score = min(tag_score / 30, 1.0)  # Normalize
    
    # User similarity (30%)
    similar_score = 0
    for similar_user in similar_users:
        if post in similar_user.liked_posts or post in similar_user.bookmarked_posts:
            similar_score += 0.1
    similar_score = min(similar_score, 1.0)
    
    # Hotness score (20%)
    hot_score = min(post.calculate_hot_score() / 100, 1.0)
    
    # Time factor (10%)
    hours_old = (datetime.utcnow() - post.created_at).total_seconds() / 3600
    time_score = max(0, 1 - hours_old / 168)  # Within a week
    
    # Combined score
    final_score = (tag_score * 0.4 + 
                  similar_score * 0.3 + 
                  hot_score * 0.2 + 
                  time_score * 0.1)
    
    return final_score


def get_recommended_posts(user=None, limit=15):
    """Get recommended posts"""
    from flask_login import current_user
    
    if not user:
        user = current_user
    
    if not user or not hasattr(user, 'is_authenticated') or not user.is_authenticated:
        return get_hot_posts(limit)
    
    # Analyze user interest tags
    user_tags = analyze_user_tags(user)
    
    # Find similar users
    similar_users = find_similar_users(user)
    
    # Get candidate posts (exclude user's own posts)
    user_post_ids = [post.id for post in user.posts]
    candidate_posts = Post.query.filter(
        ~Post.id.in_(user_post_ids),
        Post.is_draft == False
    ).all()
    
    # Calculate recommendation scores
    scored_posts = []
    for post in candidate_posts:
        score = calculate_recommendation_score(post, user, user_tags, similar_users)
        scored_posts.append((post, score))
    
    # Sort and return
    scored_posts.sort(key=lambda x: x[1], reverse=True)
    recommended = [post for post, score in scored_posts[:limit]]
    
    # If not enough recommendations, supplement with hot posts (exclude already recommended)
    if len(recommended) < limit:
        recommended_ids = {post.id for post in recommended}
        hot_posts = get_hot_posts(limit * 2)  # Get more for filtering
        # Filter out already recommended posts
        additional_posts = [post for post in hot_posts if post.id not in recommended_ids]
        recommended.extend(additional_posts[:limit - len(recommended)])
    
    # Remove duplicates (by ID)
    seen_ids = set()
    unique_recommended = []
    for post in recommended:
        if post.id not in seen_ids:
            seen_ids.add(post.id)
            unique_recommended.append(post)
    
    return unique_recommended[:limit]

