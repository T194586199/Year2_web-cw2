"""
清空数据库数据脚本
运行: python scripts/clear_data.py
警告：此操作会删除所有数据，请谨慎使用！
"""

import sys
from pathlib import Path

# 确保可以导入项目根目录下的 app 包
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app, db
from app.models import User, Post, Tag, Comment
from sqlalchemy import text

def clear_data():
    """清空所有数据"""
    app = create_app()
    with app.app_context():
        print("警告：此操作将删除所有数据！")
        confirm = input("确认删除所有数据？(输入 'yes' 确认): ")
        
        if confirm.lower() != 'yes':
            print("操作已取消")
            return
        
        print("开始清空数据...")
        
        # 删除所有数据（按依赖关系顺序）
        # 1. 删除评论（依赖帖子）
        Comment.query.delete()
        print("已删除所有评论")
        
        # 2. 删除帖子标签关联（多对多关系）
        # 需要手动删除中间表数据
        db.session.execute(text("DELETE FROM post_tags"))
        print("已删除所有帖子标签关联")
        
        # 3. 删除帖子点赞关联
        db.session.execute(text("DELETE FROM post_likes"))
        print("已删除所有帖子点赞关联")
        
        # 4. 删除评论点赞关联
        db.session.execute(text("DELETE FROM comment_likes"))
        print("已删除所有评论点赞关联")
        
        # 5. 删除收藏关联
        db.session.execute(text("DELETE FROM bookmarks"))
        print("已删除所有收藏关联")
        
        # 6. 删除关注关系
        db.session.execute(text("DELETE FROM follows"))
        print("已删除所有关注关系")
        
        # 7. 删除帖子
        Post.query.delete()
        print("已删除所有帖子")
        
        # 8. 删除标签
        Tag.query.delete()
        print("已删除所有标签")
        
        # 9. 删除用户
        User.query.delete()
        print("已删除所有用户")
        
        db.session.commit()
        
        print("\n数据清空完成！")
        print(f"用户数: {User.query.count()}")
        print(f"帖子数: {Post.query.count()}")
        print(f"标签数: {Tag.query.count()}")
        print(f"评论数: {Comment.query.count()}")

if __name__ == '__main__':
    clear_data()

