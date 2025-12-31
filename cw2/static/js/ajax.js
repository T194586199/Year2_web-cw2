// AJAX功能

// 获取CSRF Token（如果需要）
function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

// 点赞帖子
document.addEventListener('DOMContentLoaded', function() {
    const likeButtons = document.querySelectorAll('.btn-like[data-post-id]');
    likeButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const postId = this.dataset.postId;
            likePost(postId, this);
        });
    });
    
    // 收藏帖子
    const bookmarkButtons = document.querySelectorAll('.btn-bookmark[data-post-id]');
    bookmarkButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const postId = this.dataset.postId;
            bookmarkPost(postId, this);
        });
    });
    
    // 点赞评论
    const commentLikeButtons = document.querySelectorAll('.btn-comment-like[data-comment-id]');
    commentLikeButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const commentId = this.dataset.commentId;
            likeComment(commentId, this);
        });
    });
});

function likePost(postId, button) {
    fetch(`/api/post/${postId}/like`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新按钮状态
            if (data.liked) {
                button.classList.add('liked');
            } else {
                button.classList.remove('liked');
            }
            
            // 更新点赞数
            const likeCount = button.querySelector('.like-count');
            if (likeCount) {
                likeCount.textContent = data.like_count;
            }
            
            // 添加动画效果
            button.style.transform = 'scale(1.2)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 200);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('操作失败，请稍后再试');
    });
}

function bookmarkPost(postId, button) {
    fetch(`/api/post/${postId}/bookmark`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新按钮状态
            if (data.bookmarked) {
                button.classList.add('bookmarked');
                button.querySelector('span').textContent = '已收藏';
            } else {
                button.classList.remove('bookmarked');
                button.querySelector('span').textContent = '收藏';
            }
            
            // 添加动画效果
            button.style.transform = 'scale(1.2)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 200);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('操作失败，请稍后再试');
    });
}

function likeComment(commentId, button) {
    fetch(`/api/comment/${commentId}/like`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新按钮状态
            if (data.liked) {
                button.classList.add('liked');
            } else {
                button.classList.remove('liked');
            }
            
            // 更新点赞数
            const likeCount = button.querySelector('.like-count');
            if (likeCount) {
                likeCount.textContent = data.like_count;
            }
            
            // 添加动画效果
            button.style.transform = 'scale(1.2)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 200);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('操作失败，请稍后再试');
    });
}


