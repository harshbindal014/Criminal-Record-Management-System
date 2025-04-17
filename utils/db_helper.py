import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import os
from .log_config import setup_logging

class DatabaseHelper:
    _instance = None
    _db_dir = 'data'
    _db_name = 'crime_records.db'
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseHelper, cls).__new__(cls)
            cls._instance._ensure_data_dir()
            cls._instance.db_path = os.path.join(cls._db_dir, cls._db_name)
            cls._instance.logger = setup_logging('database')
        return cls._instance
    
    @classmethod
    def _ensure_data_dir(cls):
        """Ensure the data directory exists"""
        os.makedirs(cls._db_dir, exist_ok=True)
    
    @classmethod
    def get_db_path(cls):
        """Get the database path"""
        cls._ensure_data_dir()
        return os.path.join(cls._db_dir, cls._db_name)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable row factory for named columns
        try:
            yield conn
        finally:
            conn.close()
            
    def execute_query(self, query: str, params: tuple = ()) -> Optional[List[Dict[str, Any]]]:
        """Execute a query and return results as a list of dictionaries"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if query.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                else:
                    conn.commit()
                    return None
                    
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {str(e)}")
            raise
            
    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Execute many queries at once"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error in execute_many: {str(e)}")
            raise
            
    def get_single_result(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a query and return a single result"""
        results = self.execute_query(query, params)
        return results[0] if results else None
        
    def insert_and_get_id(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a record and return its ID"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, tuple(data.values()))
                conn.commit()
                return cursor.lastrowid
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error in insert_and_get_id: {str(e)}")
            raise
            
    def update_record(self, table: str, data: Dict[str, Any], condition: str, condition_params: tuple) -> None:
        """Update a record in the database"""
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        params = tuple(data.values()) + condition_params
        
        self.execute_query(query, params)
        
    def delete_record(self, table: str, condition: str, params: tuple) -> None:
        """Delete a record from the database"""
        query = f"DELETE FROM {table} WHERE {condition}"
        self.execute_query(query, params)
        
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        query = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
        """
        result = self.execute_query(query, (table_name,))
        return bool(result) 