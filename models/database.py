import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import os


class DatabaseManager:
    """数据库管理基类"""
    
    def __init__(self, db_file: str):
        self.db_file = db_file
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """初始化数据库表"""
        raise NotImplementedError


class TokenModel(DatabaseManager):
    """Web3 Alpha 代币数据模型"""
    
    def __init__(self, db_file: str = "web3_alpha.db"):
        super().__init__(db_file)
    
    def init_db(self):
        """初始化代币表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                name TEXT,
                icon_url TEXT,
                rank INTEGER,
                alpha_score REAL,
                heat_level INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS narratives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mention_count INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hashtags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag TEXT NOT NULL,
                count INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_tokens(self, tokens_data: List[Dict[str, Any]]):
        """保存代币数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for data in tokens_data:
            cursor.execute("""
                INSERT OR REPLACE INTO tokens 
                (symbol, name, icon_url, rank, alpha_score, heat_level, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["symbol"],
                data.get("name", ""),
                data.get("icon_url", ""),
                data.get("rank", 0),
                data.get("alpha_score", 0),
                data.get("heat_level", 0),
                now,
                now
            ))
        
        conn.commit()
        conn.close()
    
    def save_narratives(self, narratives_data: Dict[str, int]):
        """保存叙事数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for name, count in narratives_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO narratives 
                (name, mention_count, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (name, count, now, now))
        
        conn.commit()
        conn.close()
    
    def save_hashtags(self, hashtags_data: Dict[str, int]):
        """保存标签数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for tag, count in hashtags_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO hashtags 
                (tag, count, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (tag, count, now, now))
        
        conn.commit()
        conn.close()
    
    def get_tokens_by_time_range(self, start_time: str, limit: int = 100) -> List[Dict[str, Any]]:
        """按时间范围获取代币数据（按symbol去重，取最新记录）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT t.symbol, t.name, t.icon_url, t.rank, t.alpha_score, t.heat_level, t.created_at 
            FROM tokens t
            INNER JOIN (
                SELECT symbol, MAX(updated_at) as max_updated
                FROM tokens
                WHERE updated_at >= ?
                GROUP BY symbol
            ) latest ON t.symbol = latest.symbol AND t.updated_at = latest.max_updated
            ORDER BY t.alpha_score DESC 
            LIMIT ?
        """
        
        cursor.execute(query, (start_time, limit))
        tokens = cursor.fetchall()
        
        conn.close()
        
        return [dict(token) for token in tokens]
    
    def get_narratives(self) -> List[Dict[str, Any]]:
        """获取叙事数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, mention_count, updated_at 
            FROM narratives 
            ORDER BY mention_count DESC
        """)
        
        narratives = cursor.fetchall()
        conn.close()
        
        return [dict(narrative) for narrative in narratives]
    
    def get_hashtags(self) -> List[Dict[str, Any]]:
        """获取标签数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tag, count, updated_at 
            FROM hashtags 
            ORDER BY count DESC
        """)
        
        hashtags = cursor.fetchall()
        conn.close()
        
        return [dict(tag) for tag in hashtags]


class WebMonitorModel(DatabaseManager):
    """Web监控数据模型"""
    
    def __init__(self, db_file: str = "web_monitor.db"):
        super().__init__(db_file)
    
    def init_db(self):
        """初始化监控表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                content TEXT,
                hash TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS page_elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER,
                element_type TEXT NOT NULL,
                element_id TEXT,
                element_class TEXT,
                element_content TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (page_id) REFERENCES web_pages(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_page(self, url: str, content: str, content_hash: str):
        """保存页面数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT OR REPLACE INTO web_pages 
            (url, content, hash, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (url, content, content_hash, now, now))
        
        conn.commit()
        conn.close()
    
    def save_element(self, page_id: int, element_type: str, element_id: str, 
                   element_class: str, element_content: str):
        """保存页面元素数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT OR REPLACE INTO page_elements 
            (page_id, element_type, element_id, element_class, element_content, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (page_id, element_type, element_id, element_class, element_content, now, now))
        
        conn.commit()
        conn.close()
    
    def get_page_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """根据URL获取页面数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, url, content, hash, created_at, updated_at 
            FROM web_pages 
            WHERE url = ?
        """, (url,))
        
        page = cursor.fetchone()
        conn.close()
        
        return dict(page) if page else None
    
    def get_elements_by_page_id(self, page_id: int) -> List[Dict[str, Any]]:
        """根据页面ID获取元素数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT element_type, element_id, element_class, element_content 
            FROM page_elements 
            WHERE page_id = ?
        """, (page_id,))
        
        elements = cursor.fetchall()
        conn.close()
        
        return [dict(element) for element in elements]
