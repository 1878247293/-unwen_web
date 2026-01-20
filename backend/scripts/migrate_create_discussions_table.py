"""
创建 discussions 表和 system_settings 表的数据库迁移脚本

discussions 表用于存储公共讨论帖子
system_settings 表用于存储系统设置（如是否允许匿名）
"""

import sqlite3
from datetime import datetime

def migrate():
    # 连接数据库
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()

    try:
        print("开始创建 discussions 表...")

        # 创建 discussions 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discussions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                content TEXT NOT NULL,
                is_anonymous INTEGER DEFAULT 0,
                is_hidden INTEGER DEFAULT 0,
                parent_id INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                deleted_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL,
                FOREIGN KEY (parent_id) REFERENCES discussions (id) ON DELETE CASCADE
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discussions_user_id ON discussions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discussions_parent_id ON discussions(parent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discussions_created_at ON discussions(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discussions_is_hidden ON discussions(is_hidden)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discussions_deleted_at ON discussions(deleted_at)")

        print("✅ discussions 表创建成功")

        print("开始创建 system_settings 表...")

        # 创建 system_settings 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT NOT NULL UNIQUE,
                setting_value TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_settings_key ON system_settings(setting_key)")

        print("✅ system_settings 表创建成功")

        # 插入默认设置
        print("插入默认系统设置...")
        now = datetime.utcnow().isoformat()

        cursor.execute("""
            INSERT OR IGNORE INTO system_settings (setting_key, setting_value, description, created_at)
            VALUES (?, ?, ?, ?)
        """, ('allow_anonymous_discussion', 'true', '是否允许匿名发表讨论', now))

        print("✅ 默认设置插入成功")

        # 提交事务
        conn.commit()
        print("\n✅ 数据库迁移完成！")

        # 显示表信息
        cursor.execute("SELECT COUNT(*) FROM discussions")
        discussions_count = cursor.fetchone()[0]
        print(f"📊 discussions 表记录数: {discussions_count}")

        cursor.execute("SELECT COUNT(*) FROM system_settings")
        settings_count = cursor.fetchone()[0]
        print(f"📊 system_settings 表记录数: {settings_count}")

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
