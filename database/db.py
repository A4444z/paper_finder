# 数据库操作模块

import sqlite3
import json
import os
from datetime import datetime

class Database:
    """数据库操作类"""
    
    def __init__(self, db_path):
        """初始化数据库
        
        Args:
            db_path (str): 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
    
    def _get_connection(self):
        """获取数据库连接
        
        Returns:
            sqlite3.Connection: 数据库连接
        """
        if self.conn is None:
            # 确保数据库目录存在
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def init_db(self):
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 创建搜索历史表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keywords TEXT NOT NULL,
            sources TEXT NOT NULL,
            result_count INTEGER NOT NULL,
            search_time TIMESTAMP NOT NULL
        )
        ''')
        
        # 创建保存的文献表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_papers (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            abstract TEXT,
            authors TEXT,
            journal TEXT,
            pub_date TEXT,
            doi TEXT,
            source TEXT NOT NULL,
            keywords TEXT,
            save_time TIMESTAMP NOT NULL,
            full_data TEXT
        )
        ''')
        
        # 创建用户问题表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            related_papers TEXT,
            question_time TIMESTAMP NOT NULL
        )
        ''')
        
        conn.commit()
    
    def save_search_history(self, keywords, sources, result_count):
        """保存搜索历史
        
        Args:
            keywords (str): 搜索关键词
            sources (list): 搜索来源列表
            result_count (int): 结果数量
            
        Returns:
            int: 新记录的ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 将来源列表转换为JSON字符串
        sources_json = json.dumps(sources)
        
        cursor.execute(
            'INSERT INTO search_history (keywords, sources, result_count, search_time) VALUES (?, ?, ?, ?)',
            (keywords, sources_json, result_count, datetime.now().isoformat())
        )
        
        conn.commit()
        return cursor.lastrowid
    
    def get_search_history(self, limit=20):
        """获取搜索历史
        
        Args:
            limit (int, optional): 最大记录数
            
        Returns:
            list: 搜索历史记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM search_history ORDER BY search_time DESC LIMIT ?',
            (limit,)
        )
        
        results = []
        for row in cursor.fetchall():
            history = dict(row)
            # 将JSON字符串转换回列表
            history['sources'] = json.loads(history['sources'])
            results.append(history)
        
        return results
    
    def save_paper(self, paper):
        """保存文献
        
        Args:
            paper (dict): 文献信息
            
        Returns:
            bool: 是否保存成功
        """
        if not paper or 'id' not in paper:
            return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 检查文献是否已存在
        cursor.execute('SELECT id FROM saved_papers WHERE id = ?', (paper['id'],))
        if cursor.fetchone():
            # 更新现有记录
            cursor.execute(
                '''
                UPDATE saved_papers SET 
                    title = ?, 
                    abstract = ?, 
                    authors = ?, 
                    journal = ?, 
                    pub_date = ?, 
                    doi = ?, 
                    source = ?, 
                    keywords = ?, 
                    save_time = ?, 
                    full_data = ?
                WHERE id = ?
                ''',
                (
                    paper.get('title', ''),
                    paper.get('abstract', ''),
                    json.dumps(paper.get('authors', [])),
                    paper.get('journal', ''),
                    paper.get('pub_date', ''),
                    paper.get('doi', ''),
                    paper.get('source', ''),
                    json.dumps(paper.get('keywords', [])),
                    datetime.now().isoformat(),
                    json.dumps(paper),
                    paper['id']
                )
            )
        else:
            # 插入新记录
            cursor.execute(
                '''
                INSERT INTO saved_papers (
                    id, title, abstract, authors, journal, pub_date, doi, source, keywords, save_time, full_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    paper['id'],
                    paper.get('title', ''),
                    paper.get('abstract', ''),
                    json.dumps(paper.get('authors', [])),
                    paper.get('journal', ''),
                    paper.get('pub_date', ''),
                    paper.get('doi', ''),
                    paper.get('source', ''),
                    json.dumps(paper.get('keywords', [])),
                    datetime.now().isoformat(),
                    json.dumps(paper)
                )
            )
        
        conn.commit()
        return True
    
    def get_saved_papers(self, limit=100):
        """获取保存的文献
        
        Args:
            limit (int, optional): 最大记录数
            
        Returns:
            list: 保存的文献列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM saved_papers ORDER BY save_time DESC LIMIT ?',
            (limit,)
        )
        
        results = []
        for row in cursor.fetchall():
            paper = dict(row)
            # 将JSON字符串转换回列表或字典
            paper['authors'] = json.loads(paper['authors'])
            paper['keywords'] = json.loads(paper['keywords'])
            paper['full_data'] = json.loads(paper['full_data'])
            results.append(paper)
        
        return results
    
    def get_paper(self, paper_id):
        """获取单篇保存的文献
        
        Args:
            paper_id (str): 文献ID
            
        Returns:
            dict: 文献信息
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM saved_papers WHERE id = ?', (paper_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        paper = dict(row)
        # 将JSON字符串转换回列表或字典
        paper['authors'] = json.loads(paper['authors'])
        paper['keywords'] = json.loads(paper['keywords'])
        paper['full_data'] = json.loads(paper['full_data'])
        
        return paper
    
    def delete_paper(self, paper_id):
        """删除保存的文献
        
        Args:
            paper_id (str): 文献ID
            
        Returns:
            bool: 是否删除成功
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM saved_papers WHERE id = ?', (paper_id,))
        conn.commit()
        
        return cursor.rowcount > 0
    
    def save_question(self, question, answer, related_papers=None):
        """保存用户问题和回答
        
        Args:
            question (str): 问题
            answer (str): 回答
            related_papers (list, optional): 相关文献ID列表
            
        Returns:
            int: 新记录的ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 将相关文献列表转换为JSON字符串
        related_papers_json = json.dumps(related_papers) if related_papers else '[]'
        
        cursor.execute(
            'INSERT INTO user_questions (question, answer, related_papers, question_time) VALUES (?, ?, ?, ?)',
            (question, answer, related_papers_json, datetime.now().isoformat())
        )
        
        conn.commit()
        return cursor.lastrowid
    
    def get_questions(self, limit=20):
        """获取用户问题历史
        
        Args:
            limit (int, optional): 最大记录数
            
        Returns:
            list: 问题历史记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM user_questions ORDER BY question_time DESC LIMIT ?',
            (limit,)
        )
        
        results = []
        for row in cursor.fetchall():
            question = dict(row)
            # 将JSON字符串转换回列表
            question['related_papers'] = json.loads(question['related_papers'])
            results.append(question)
        
        return results
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None