from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Post, Tag, Comment
from app.forms import RegistrationForm, LoginForm, PostForm, CommentForm, UserSettingsForm, PasswordChangeForm
from app.utils import render_markdown, time_ago, get_recommended_posts, get_hot_posts, get_text_preview, get_avatar_url, get_category_display
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import re

# Main blueprints
main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
api = Blueprint('api', __name__)


# ==================== Main Routes ====================

@main.route('/')
def index():
    """Homepage"""
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'latest')
    category = request.args.get('category', '')
    tag_name = request.args.get('tag', '')
    
    # Build query
    query = Post.query.filter_by(is_draft=False)
    
    # Category filter - handle both English and Chinese category names
    if category:
        # Map category to handle both English and Chinese
        category_map = {
            'Technique': ['Technique', '技术'],
            'Equipment': ['Equipment', '装备'],
            'Tournament': ['Tournament', '比赛'],
            'Training': ['Training', '训练'],
            'Other': ['Other', '其他']
        }
        # Get all possible category values for the selected category
        category_values = category_map.get(category, [category])
        query = query.filter(Post.category.in_(category_values))
    
    # Tag filter
    if tag_name:
        tag = Tag.query.filter_by(name=tag_name).first()
        if tag:
            query = query.filter(Post.tags.contains(tag))
    
    # Sorting
    if sort == 'comments':
        query = query.order_by(Post.comment_count.desc())
    elif sort == 'likes':
        query = query.order_by(Post.like_count.desc())
    elif sort == 'views':
        query = query.order_by(Post.view_count.desc())
    elif sort == 'hot':
        # Hot sorting requires special handling
        posts = query.all()
        scored_posts = [(p, p.calculate_hot_score()) for p in posts]
        scored_posts.sort(key=lambda x: x[1], reverse=True)
        pagination = None
        posts = [p for p, s in scored_posts]
        total = len(posts)
        start = (page - 1) * 20
        end = start + 20
        posts = posts[start:end]
    else:  # latest
        query = query.order_by(Post.created_at.desc())
    
    if sort != 'hot':
        pagination = query.paginate(page=page, per_page=20, error_out=False)
        posts = pagination.items
    else:
        pagination = type('obj', (object,), {
            'page': page,
            'pages': (total + 19) // 20,
            'total': total,
            'has_prev': page > 1,
            'has_next': end < total
        })()
    
    # Get recommended posts (if user is logged in)
    recommended_posts = []
    if current_user.is_authenticated:
        recommended_posts = get_recommended_posts(user=current_user, limit=5)
    else:
        recommended_posts = get_hot_posts(limit=5)
    
    # Get popular tags (tags used at least once)
    hot_tags = Tag.query.filter(Tag.usage_count > 0).order_by(Tag.usage_count.desc()).limit(10).all()
    
    return render_template('index.html', 
                         posts=posts, 
                         pagination=pagination,
                         sort=sort,
                         category=category,
                         tag_name=tag_name,
                         recommended_posts=recommended_posts,
                         hot_tags=hot_tags,
                         time_ago=time_ago,
                         get_text_preview=get_text_preview,
                         get_category_display=get_category_display)


@main.route('/post/<int:post_id>')
def post_detail(post_id):
    """Post detail"""
    post = Post.query.get_or_404(post_id)
    
    # Increment view count
    post.increment_view()
    
    # Get comments (excluding deleted ones)
    comments = Comment.query.filter_by(
        post_id=post_id, 
        is_deleted=False,
        parent_id=None
    ).order_by(Comment.created_at.desc()).all()
    
    # Get related posts (based on tags)
    related_posts = []
    if post.tags.count() > 0:
        related_query = Post.query.filter(
            Post.id != post_id,
            Post.is_draft == False
        ).join(Post.tags).filter(
            Tag.id.in_([tag.id for tag in post.tags])
        ).distinct().limit(5).all()
        related_posts = related_query
    
    form = CommentForm()
    
    return render_template('post_detail.html',
                         post=post,
                         comments=comments,
                         related_posts=related_posts,
                         form=form,
                         render_markdown=render_markdown,
                         time_ago=time_ago,
                         get_category_display=get_category_display)


@main.route('/post/create', methods=['GET', 'POST'])
@login_required
def post_create():
    """Create post"""
    form = PostForm()
    
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user,
            category=form.category.data,
            is_draft=bool(request.form.get('save_draft'))
        )
        
        # Process tags
        tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
        # Remove duplicates, maintain order
        seen = set()
        unique_tag_names = []
        for tag_name in tag_names[:5]:  # Maximum 5 tags
            if tag_name and tag_name not in seen:
                seen.add(tag_name)
                unique_tag_names.append(tag_name)
        
        for tag_name in unique_tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            if tag not in post.tags:
                post.tags.append(tag)
                tag.increment_usage()
        
        db.session.add(post)
        db.session.commit()
        
        flash('Post published successfully!', 'success')
        return redirect(url_for('main.post_detail', post_id=post.id))
    
    # Get all tags for autocomplete
    all_tags = Tag.query.order_by(Tag.usage_count.desc()).limit(100).all()
    
    return render_template('post_create.html', form=form, all_tags=all_tags)


@main.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def post_edit(post_id):
    """Edit post"""
    post = Post.query.get_or_404(post_id)
    
    if post.author != current_user:
        abort(403)
    
    form = PostForm()
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        post.updated_at = datetime.utcnow()
        
        # Update tags
        old_tags = list(post.tags)
        old_tag_names = {tag.name for tag in old_tags}
        
        # Remove tags that are no longer used
        tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
        new_tag_names = set(tag_names[:5])
        
        # Find tags to remove (in old tags but not in new tags)
        tags_to_remove = old_tag_names - new_tag_names
        for tag in old_tags:
            if tag.name in tags_to_remove:
                post.tags.remove(tag)
                tag.decrement_usage()
        
        # Add new tags (only add those not in old tags)
        tags_to_add = new_tag_names - old_tag_names
        for tag_name in tags_to_add:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            if tag not in post.tags:
                post.tags.append(tag)
                tag.increment_usage()
        
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('main.post_detail', post_id=post.id))
    
    # 预填充表单
    form.title.data = post.title
    form.content.data = post.content
    form.category.data = post.category
    form.tags.data = ', '.join([tag.name for tag in post.tags])
    
    all_tags = Tag.query.order_by(Tag.usage_count.desc()).limit(100).all()
    
    return render_template('post_create.html', form=form, post=post, all_tags=all_tags)


@main.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def post_delete(post_id):
    """Delete post"""
    post = Post.query.get_or_404(post_id)
    
    if post.author != current_user:
        abort(403)
    
    # Remove tag associations
    for tag in list(post.tags):
        post.tags.remove(tag)
        tag.decrement_usage()
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Post deleted', 'success')
    return redirect(url_for('main.index'))


@main.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def comment_create(post_id):
    """Create comment"""
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        parent_id = form.parent_id.data
        parent = None
        if parent_id:
            parent = Comment.query.get(int(parent_id))
            if parent and parent.get_depth() >= 2:
                flash('Comment nesting depth cannot exceed 3 levels', 'error')
                return redirect(url_for('main.post_detail', post_id=post_id))
        
        comment = Comment(
            post=post,
            author=current_user,
            content=form.content.data,
            parent=parent
        )
        
        post.comment_count += 1
        db.session.add(comment)
        db.session.commit()
        
        flash('Comment posted successfully!', 'success')
    
    return redirect(url_for('main.post_detail', post_id=post_id))


@main.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
def comment_edit(comment_id):
    """Edit comment"""
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.author != current_user:
        abort(403)
    
    if request.method == 'POST':
        comment.content = request.form.get('content')
        comment.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Comment updated successfully!', 'success')
        return redirect(url_for('main.post_detail', post_id=comment.post_id))
    
    return render_template('comment_edit.html', comment=comment)


@main.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def comment_delete(comment_id):
    """Delete comment (soft delete)"""
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.author != current_user:
        abort(403)
    
    comment.is_deleted = True
    comment.post.comment_count -= 1
    db.session.commit()
    
    flash('Comment deleted', 'success')
    return redirect(url_for('main.post_detail', post_id=comment.post_id))


@main.route('/tag/<tag_name>')
def tag_detail(tag_name):
    """Tag detail page"""
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'latest')
    
    query = Post.query.filter(
        Post.is_draft == False,
        Post.tags.contains(tag)
    )
    
    if sort == 'comments':
        query = query.order_by(Post.comment_count.desc())
    elif sort == 'likes':
        query = query.order_by(Post.like_count.desc())
    elif sort == 'views':
        query = query.order_by(Post.view_count.desc())
    else:
        query = query.order_by(Post.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    posts = pagination.items
    
    return render_template('tag_detail.html',
                         tag=tag,
                         posts=posts,
                         pagination=pagination,
                         sort=sort,
                         time_ago=time_ago,
                         get_category_display=get_category_display)


@main.route('/user/<username>')
def user_profile(username):
    """User profile"""
    user = User.query.filter_by(username=username).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    tab = request.args.get('tab', 'posts')
    
    if tab == 'posts':
        pagination = user.posts.filter_by(is_draft=False).order_by(
            Post.created_at.desc()
        ).paginate(page=page, per_page=20, error_out=False)
        items = pagination.items
    elif tab == 'bookmarks' and current_user == user:
        pagination = user.bookmarked_posts.filter_by(is_draft=False).order_by(
            Post.created_at.desc()
        ).paginate(page=page, per_page=20, error_out=False)
        items = pagination.items
    else:
        pagination = None
        items = []
    
    # Statistics
    stats = {
        'posts_count': user.posts.filter_by(is_draft=False).count(),
        'comments_count': user.comments.filter_by(is_deleted=False).count(),
        'following_count': user.following.count(),
        'followers_count': user.followers.count()
    }
    
    is_following = False
    if current_user.is_authenticated and current_user != user:
        is_following = current_user.is_following(user)
    
    return render_template('user_profile.html',
                         user=user,
                         items=items,
                         pagination=pagination,
                         tab=tab,
                         stats=stats,
                         is_following=is_following,
                         time_ago=time_ago,
                         get_avatar_url=get_avatar_url,
                         get_category_display=get_category_display)


@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings"""
    form = UserSettingsForm()
    password_form = PasswordChangeForm()
    
    # Handle avatar upload (separate handling)
    if request.method == 'POST' and request.form.get('update_avatar'):
        # Get file directly from request.files to avoid form validation issues
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                # Check file extension (from original filename, without secure_filename processing)
                original_filename = file.filename
                if '.' not in original_filename:
                    flash('File format not supported. Please upload JPG, PNG or GIF images', 'error')
                    return render_template('user_settings.html', form=form, password_form=password_form)
                
                file_ext = original_filename.rsplit('.', 1)[1].lower()
                # Unify jpg and jpeg
                if file_ext == 'jpeg':
                    file_ext = 'jpg'
                
                # Check extension (after unification)
                allowed_exts = {'png', 'jpg', 'gif'}
                if file_ext not in allowed_exts:
                    flash(f'File format not supported (current: .{file_ext}). Please upload JPG, PNG or GIF images', 'error')
                    return render_template('user_settings.html', form=form, password_form=password_form)
                
                # Check file size
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                if file_size > current_app.config['MAX_AVATAR_SIZE']:
                    flash('Image file too large. Please upload an image smaller than 2MB', 'error')
                    return render_template('user_settings.html', form=form, password_form=password_form)
                
                # Ensure upload directory exists
                upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
                upload_folder.mkdir(parents=True, exist_ok=True)
                
                # Use user ID and current timestamp to ensure uniqueness
                new_filename = f'avatar_{current_user.id}_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.{file_ext}'
                filepath = upload_folder / new_filename
                
                # Save file
                file.save(str(filepath))
                
                # Delete old avatar (if not default avatar)
                if current_user.avatar_url and current_user.avatar_url != 'default_avatar.png':
                    old_avatar_path = upload_folder / current_user.avatar_url
                    if old_avatar_path.exists():
                        try:
                            old_avatar_path.unlink()
                        except:
                            pass  # Ignore deletion errors
                
                # Update user avatar URL (only save filename, not path)
                current_user.avatar_url = new_filename
                db.session.commit()
                flash('Avatar uploaded successfully!', 'success')
                return redirect(url_for('main.settings'))
        else:
            flash('Please select an image to upload', 'error')
    
    if form.validate_on_submit() and not request.form.get('update_avatar'):
        # Check if username and email are used by other users
        if form.username.data != current_user.username:
            if User.query.filter(User.username == form.username.data, 
                               User.id != current_user.id).first():
                flash('This username is already taken', 'error')
                return render_template('user_settings.html', form=form, password_form=password_form)
        
        if form.email.data != current_user.email:
            if User.query.filter(User.email == form.email.data, 
                               User.id != current_user.id).first():
                flash('This email is already registered', 'error')
                return render_template('user_settings.html', form=form, password_form=password_form)
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Settings updated', 'success')
        return redirect(url_for('main.settings'))
    
    if password_form.validate_on_submit():
        if not current_user.check_password(password_form.old_password.data):
            flash('Current password is incorrect', 'error')
            return render_template('user_settings.html', form=form, password_form=password_form)
        
        current_user.set_password(password_form.new_password.data)
        db.session.commit()
        flash('Password updated', 'success')
        return redirect(url_for('main.settings'))
    
    # Pre-fill form
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.bio.data = current_user.bio
    
    return render_template('user_settings.html', form=form, password_form=password_form)


@main.route('/search')
def search():
    """Search"""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return render_template('search.html', query=query, posts=[], pagination=None, get_text_preview=get_text_preview, get_category_display=get_category_display)
    
    # Search post titles and content
    posts = Post.query.filter(
        Post.is_draft == False,
        (Post.title.contains(query) | Post.content.contains(query))
    ).order_by(Post.created_at.desc())
    
    pagination = posts.paginate(page=page, per_page=20, error_out=False)
    posts = pagination.items
    
    return render_template('search.html',
                         query=query,
                         posts=posts,
                         pagination=pagination,
                         time_ago=time_ago,
                         get_text_preview=get_text_preview,
                         get_category_display=get_category_display)


@main.route('/user/<username>/follow', methods=['POST'])
@login_required
def follow_user(username):
    """Follow user"""
    user = User.query.filter_by(username=username).first_or_404()
    
    if user == current_user:
        flash('You cannot follow yourself', 'error')
        return redirect(url_for('main.user_profile', username=username))
    
    if current_user.follow(user):
        db.session.commit()
        flash(f'Now following {user.username}', 'success')
    else:
        flash('You are already following this user', 'info')
    
    return redirect(url_for('main.user_profile', username=username))


@main.route('/user/<username>/unfollow', methods=['POST'])
@login_required
def unfollow_user(username):
    """Unfollow user"""
    user = User.query.filter_by(username=username).first_or_404()
    
    if current_user.unfollow(user):
        db.session.commit()
        flash(f'Unfollowed {user.username}', 'success')
    
    return redirect(url_for('main.user_profile', username=username))


# ==================== Authentication Routes ====================

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Register"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful! Welcome!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Support login with username or email
        user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.username.data)
        ).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data == '1')
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
        
        flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('main.index'))


# ==================== API Routes ====================

@api.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    """Like post (AJAX)"""
    post = Post.query.get_or_404(post_id)
    
    if current_user in post.liked_by:
        post.liked_by.remove(current_user)
        post.like_count -= 1
        liked = False
    else:
        post.liked_by.append(current_user)
        post.like_count += 1
        liked = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'liked': liked,
        'like_count': post.like_count
    })


@api.route('/post/<int:post_id>/bookmark', methods=['POST'])
@login_required
def bookmark_post(post_id):
    """Bookmark post (AJAX)"""
    post = Post.query.get_or_404(post_id)
    
    if current_user in post.bookmarked_by:
        post.bookmarked_by.remove(current_user)
        bookmarked = False
    else:
        post.bookmarked_by.append(current_user)
        bookmarked = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'bookmarked': bookmarked
    })


@api.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment(comment_id):
    """Like comment (AJAX)"""
    comment = Comment.query.get_or_404(comment_id)
    
    if current_user in comment.liked_by:
        comment.liked_by.remove(current_user)
        comment.like_count -= 1
        liked = False
    else:
        comment.liked_by.append(current_user)
        comment.like_count += 1
        liked = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'liked': liked,
        'like_count': comment.like_count
    })


@api.route('/search/suggest', methods=['GET'])
def search_suggest():
    """Search suggestions (AJAX)"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify({'suggestions': []})
    
    # 搜索标签
    tags = Tag.query.filter(Tag.name.contains(query)).limit(5).all()
    
    # 搜索帖子标题
    posts = Post.query.filter(
        Post.is_draft == False,
        Post.title.contains(query)
    ).limit(5).all()
    
    suggestions = []
    for tag in tags:
        suggestions.append({
            'type': 'tag',
            'text': tag.name,
            'url': f'/tag/{tag.name}'
        })
    for post in posts:
        suggestions.append({
            'type': 'post',
            'text': post.title,
            'url': f'/post/{post.id}'
        })
    
    return jsonify({'suggestions': suggestions[:10]})


# ==================== Error Handlers ====================

def page_not_found(e):
    return render_template('errors/404.html'), 404


def internal_error(e):
    db.session.rollback()
    return render_template('errors/500.html'), 500

