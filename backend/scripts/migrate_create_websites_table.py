"""
数据库迁移脚本：创建 websites 表

用于存储科研常用网站的信息

执行方式：
cd backend
python scripts/migrate_create_websites_table.py
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
from datetime import datetime

def migrate():
    """执行数据库迁移"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'database.db')

    print(f"数据库路径: {db_path}")

    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print("错误: 数据库文件不存在!")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查表是否已经存在
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='websites'
        """)

        if cursor.fetchone():
            print("警告: websites 表已经存在，跳过创建")
            return True

        # 创建 websites 表
        print("正在创建 websites 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS websites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                category TEXT,
                description TEXT,
                is_favorite INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                deleted_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        # 创建索引以提升查询性能
        print("正在创建索引...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_websites_user_id
            ON websites(user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_websites_category
            ON websites(category)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_websites_is_favorite
            ON websites(is_favorite)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_websites_deleted_at
            ON websites(deleted_at)
        """)

        # 插入一些默认的科研网站数据（可选）
        print("正在插入默认网站数据...")
        default_websites = [
            # 学术搜索引擎
            ('Google Scholar', 'https://scholar.google.com', '学术搜索', '最全面的学术搜索引擎，涵盖各学科领域'),
            ('Semantic Scholar', 'https://www.semanticscholar.org', '学术搜索', 'AI驱动的学术搜索引擎，提供论文影响力分析'),
            ('百度学术', 'https://xueshu.baidu.com', '学术搜索', '中文学术搜索引擎'),

            # 论文数据库
            ('arXiv', 'https://arxiv.org', '论文数据库', '预印本论文库，主要涵盖物理、数学、计算机等领域'),
            ('PubMed', 'https://pubmed.ncbi.nlm.nih.gov', '论文数据库', '生物医学文献数据库'),
            ('IEEE Xplore', 'https://ieeexplore.ieee.org', '论文数据库', 'IEEE论文数据库，涵盖电子工程和计算机科学'),
            ('ACM Digital Library', 'https://dl.acm.org', '论文数据库', 'ACM论文数据库，计算机科学领域'),
            ('ScienceDirect', 'https://www.sciencedirect.com', '论文数据库', 'Elsevier旗下的科学文献数据库'),
            ('SpringerLink', 'https://link.springer.com', '论文数据库', 'Springer出版社的学术资源平台'),
            ('中国知网', 'https://www.cnki.net', '论文数据库', '中文学术文献数据库'),
            ('万方数据', 'https://www.wanfangdata.com.cn', '论文数据库', '中文学术资源平台'),

            # 文献管理工具
            ('Zotero', 'https://www.zotero.org', '文献管理', '开源文献管理工具'),
            ('Mendeley', 'https://www.mendeley.com', '文献管理', 'Elsevier旗下的文献管理工具'),
            ('EndNote', 'https://endnote.com', '文献管理', '专业的文献管理软件'),

            # 引文分析
            ('Web of Science', 'https://www.webofscience.com', '引文分析', '权威的引文索引数据库'),
            ('Scopus', 'https://www.scopus.com', '引文分析', 'Elsevier的引文数据库'),

            # 期刊资源
            ('Journal Citation Reports', 'https://jcr.clarivate.com', '期刊资源', '期刊影响因子查询'),
            ('SCI-Hub', 'https://sci-hub.se', '期刊资源', '论文免费下载（镜像站点经常变动）'),
            ('Library Genesis', 'https://libgen.is', '期刊资源', '电子书和论文免费下载'),

            # 学术工具
            ('Connected Papers', 'https://www.connectedpapers.com', '学术工具', '论文关系图谱可视化工具'),
            ('ResearchGate', 'https://www.researchgate.net', '学术工具', '学术社交网络平台'),
            ('Academia.edu', 'https://www.academia.edu', '学术工具', '学术论文分享平台'),
            ('ORCID', 'https://orcid.org', '学术工具', '学术研究者唯一标识符'),

            # 数据集资源
            ('Kaggle', 'https://www.kaggle.com', '数据集', '机器学习竞赛和数据集平台'),
            ('UCI Machine Learning Repository', 'https://archive.ics.uci.edu/ml', '数据集', '经典机器学习数据集库'),
            ('Papers with Code', 'https://paperswithcode.com', '数据集', '论文代码和数据集整合平台'),
            ('Google Dataset Search', 'https://datasetsearch.research.google.com', '数据集', 'Google的数据集搜索引擎'),
        ]

        # 获取admin用户ID（假设admin的ID为1）
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        admin_id = admin_user[0] if admin_user else 1

        now = datetime.utcnow().isoformat()
        for name, url, category, description in default_websites:
            cursor.execute("""
                INSERT INTO websites (user_id, name, url, category, description, is_favorite, created_at)
                VALUES (?, ?, ?, ?, ?, 0, ?)
            """, (admin_id, name, url, category, description, now))

        # 提交事务
        conn.commit()
        print(f"✓ websites 表创建成功！已插入 {len(default_websites)} 条默认数据")

        # 验证表结构
        cursor.execute("PRAGMA table_info(websites)")
        columns = cursor.fetchall()
        print("\n表结构:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

        # 验证数据
        cursor.execute("SELECT COUNT(*) FROM websites WHERE deleted_at IS NULL")
        count = cursor.fetchone()[0]
        print(f"\n当前网站数量: {count}")

        return True

    except Exception as e:
        conn.rollback()
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("开始执行数据库迁移：创建 websites 表")
    print("=" * 60)

    success = migrate()

    if success:
        print("\n" + "=" * 60)
        print("✓ 迁移成功完成！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ 迁移失败")
        print("=" * 60)
        sys.exit(1)
