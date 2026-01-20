"""
创建讨论互动功能表的数据库迁移脚本

discussion_likes 表用于存储点赞记录
discussion_favorites 表用于存储收藏记录
discussion_reports 表用于存储举报记录
"""

import sqlite3
from datetime import datetime

def migrate():
    # 连接数据库
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()

    try:
        print("开始创建 discussion_likes 表...")

        # 创建 discussion_likes 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discussion_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discussion_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (discussion_id) REFERENCES discussions (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE (discussion_id, user_id)
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discussion_likes_discussion_id ON discussion_likes(discussion_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discussion_likes_user_id ON discussion_likes(user_id)")

        print("✅ discussion_likes 表创建成功")

        print("开始创建 discussion_favorites 表...")

        # 创建 discussion_favorites 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discussion_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discussion_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (discussion_id) REFERENCES discussions (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE (discussion_id, user_id)
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discussion_favorites_discussion_id ON discussion_favorites(discussion_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discussion_favorites_user_id ON discussion_favorites(user_id)")

        print("✅ discussion_favorites 表创建成功")

        print("开始创建 discussion_reports 表...")

        # 创建 discussion_reports 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discussion_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discussion_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                handled_at TEXT,
                handled_by INTEGER,
                FOREIGN KEY (discussion_id) REFERENCES discussions (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (handled_by) REFERENCES users (id) ON DELETE SET NULL
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discussion_reports_discussion_id ON discussion_reports(discussion_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discussion_reports_user_id ON discussion_reports(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discussion_reports_status ON discussion_reports(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discussion_reports_handled_by ON discussion_reports(handled_by)")

        print("✅ discussion_reports 表创建成功")

        # 提交事务
        conn.commit()
        print("\n✅ 数据库迁移完成！")

        # 显示表信息
        cursor.execute("SELECT COUNT(*) FROM discussion_likes")
        likes_count = cursor.fetchone()[0]
        print(f"📊 discussion_likes 表记录数: {likes_count}")

        cursor.execute("SELECT COUNT(*) FROM discussion_favorites")
        favorites_count = cursor.fetchone()[0]
        print(f"📊 discussion_favorites 表记录数: {favorites_count}")

        cursor.execute("SELECT COUNT(*) FROM discussion_reports")
        reports_count = cursor.fetchone()[0]
        print(f"📊 discussion_reports 表记录数: {reports_count}")

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
