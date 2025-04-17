from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import bcrypt
import sqlite3
import logging
import os
from .base_model import BaseModel
from utils.db_helper import DatabaseHelper

class UserModel(BaseModel):
    table_name = "users"
    
    def __init__(self):
        super().__init__()
        self.searchable_fields = ['username']
        self.db_path = os.path.join('data', 'crime_records.db')
    
    def get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path)
    
    def create_user(self, username: str, password: str, role: str = 'user') -> bool:
        """Create a new user"""
        try:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            query = "INSERT INTO users (username, password, role) VALUES (?, ?, ?)"
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (username, hashed, role))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error creating user: {str(e)}")
            return False
            
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate a user with username and password"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            
            if user:
                stored_password = user[2].encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    # Update last login time
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute(
                        'UPDATE users SET last_login = ? WHERE id = ?',
                        (now, user[0])
                    )
                    conn.commit()
                    
                    return {
                        'id': user[0],
                        'username': user[1],
                        'role': user[3],
                        'last_login': now
                    }
            return None
            
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()
            
    def get_user(self, user_id: int) -> Optional[Tuple]:
        """Get user by ID"""
        try:
            query = "SELECT * FROM users WHERE id = ?"
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        except Exception as e:
            logging.error(f'Error getting user: {str(e)}')
            return None
            
    def get_all_users(self) -> list:
        """Get all users"""
        try:
            query = "SELECT id, username, role FROM users"
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            logging.error(f'Error getting users: {str(e)}')
            return []
            
    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        try:
            query = "DELETE FROM users WHERE id = ?"
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            conn.commit()
            logging.info(f'Deleted user ID: {user_id}')
            return True
        except Exception as e:
            logging.error(f'Error deleting user: {str(e)}')
            return False
            
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user's password"""
        user = self.get_user(user_id)
        if not user:
            return False
            
        # Verify current password
        if not bcrypt.checkpw(current_password.encode('utf-8'), user['password']):
            return False
            
        # Update password
        return self.update_password(user_id, new_password)
    
    def update_password(self, user_id: int, new_password: str) -> bool:
        """Update user's password"""
        try:
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            query = "UPDATE users SET password = ? WHERE id = ?"
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (hashed, user_id))
            conn.commit()
            logging.info(f'Updated password for user ID: {user_id}')
            return True
        except Exception as e:
            logging.error(f'Error updating password: {str(e)}')
            return False
    
    def get_all_officers(self) -> List[Dict[str, Any]]:
        """Get all users with officer role"""
        return self.db.execute_query(
            f"SELECT id, username, created_at, last_login FROM {self.table_name} WHERE role = ?",
            ('officer',)
        )
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        total = self.count()
        
        role_stats = self.db.execute_query("""
            SELECT role, COUNT(*) as count
            FROM users
            GROUP BY role
        """)
        
        active_users = self.db.execute_query("""
            SELECT COUNT(*) as count
            FROM users
            WHERE last_login >= datetime('now', '-7 days')
        """)[0]['count']
        
        return {
            'total_users': total,
            'role_stats': role_stats,
            'active_users_last_7_days': active_users
        }
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user has admin role"""
        user = self.get_user(user_id)
        return user and user['role'] == 'admin' 