// 主JavaScript文件

document.addEventListener('DOMContentLoaded', function() {
    // 移动端菜单切换
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navbarNav = document.querySelector('.navbar-nav');
    
    if (mobileMenuToggle && navbarNav) {
        mobileMenuToggle.addEventListener('click', function() {
            navbarNav.classList.toggle('show');
            const isExpanded = navbarNav.classList.contains('show');
            this.setAttribute('aria-expanded', isExpanded);
        });
    }
    
    // 关闭提示消息
    const alertCloses = document.querySelectorAll('.alert-close');
    alertCloses.forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.alert').style.display = 'none';
        });
    });
    
    // 自动隐藏提示消息（5秒后）
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 500);
        }, 5000);
    });
    
    // 返回顶部按钮（如果存在）
    const backToTop = document.querySelector('.back-to-top');
    if (backToTop) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTop.style.display = 'block';
            } else {
                backToTop.style.display = 'none';
            }
        });
        
        backToTop.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // 评论回复功能
    const replyButtons = document.querySelectorAll('.btn-reply');
    replyButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const parentId = this.dataset.parentId;
            const commentForm = document.querySelector('.comment-form');
            if (commentForm) {
                const parentIdInput = commentForm.querySelector('input[name="parent_id"]');
                if (parentIdInput) {
                    parentIdInput.value = parentId;
                }
                
                // 滚动到表单
                commentForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
                const textarea = commentForm.querySelector('textarea');
                if (textarea) {
                    textarea.focus();
                    textarea.value = `@${this.closest('.comment-item').querySelector('.comment-author').textContent} `;
                }
            }
        });
    });
});


