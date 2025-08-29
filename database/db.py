# paper_finder/database/db.py

import sqlite3
import os
from datetime import datetime

class Database:
    """数据库管理类，采用按需连接的方式以确保线程安全"""

    def __init__(self, db_path):
        """
        初始化数据库类。
        Args:
            db_path (str): 数据库文件路径。
        """
        self.db_path = db_path
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def get_db_conn(self):
        """
        获取一个新的数据库连接。
        每次需要操作数据库时都应该调用此方法。
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # 让查询结果可以像字典一样访问
        return conn

    def init_db(self):
        """
        初始化数据库表结构。
        如果表已存在，则不会重复创建。
        """
        conn = self.get_db_conn()
        try:
            with conn: # 使用 with 语句可以自动提交或回滚事务
                cursor = conn.cursor()
                # 创建搜索历史表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS search_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        keywords TEXT NOT NULL,
                        sources TEXT NOT NULL,
                        result_count INTEGER NOT NULL,
                        search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
        finally:
            conn.close() # 确保连接被关闭

    def save_search_history(self, keywords, sources, result_count):
        """
        保存一条搜索历史记录。
        """
        # 将来源列表转换为字符串
        sources_str = ','.join(sources)
        
        conn = self.get_db_conn()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO search_history (keywords, sources, result_count, search_time)
                    VALUES (?, ?, ?, ?)
                """, (keywords, sources_str, result_count, datetime.now()))
        except sqlite3.Error as e:
            print(f"数据库保存历史记录时出错: {e}")
        finally:
            conn.close()

    def get_search_history(self, limit=50):
        """
        获取最近的搜索历史记录。
        """
        conn = self.get_db_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM search_history ORDER BY search_time DESC LIMIT ?", (limit,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"数据库获取历史记录时出错: {e}")
            return []
        finally:
            conn.close()