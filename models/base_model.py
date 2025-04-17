from typing import Dict, List, Optional, Any
from utils.db_helper import DatabaseHelper

class BaseModel:
    table_name: str = ""
    primary_key: str = "id"
    
    def __init__(self):
        self.db = DatabaseHelper()
    
    def create(self, data: Dict[str, Any]) -> int:
        """Create a new record"""
        return self.db.insert_and_get_id(self.table_name, data)
    
    def update(self, id: int, data: Dict[str, Any]) -> None:
        """Update an existing record"""
        self.db.update_record(
            self.table_name,
            data,
            f"{self.primary_key} = ?",
            (id,)
        )
    
    def delete(self, id: int) -> None:
        """Delete a record"""
        self.db.delete_record(
            self.table_name,
            f"{self.primary_key} = ?",
            (id,)
        )
    
    def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """Get a record by ID"""
        return self.db.get_single_result(
            f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?",
            (id,)
        )
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all records"""
        return self.db.execute_query(f"SELECT * FROM {self.table_name}")
    
    def get_by_field(self, field: str, value: Any) -> List[Dict[str, Any]]:
        """Get records by field value"""
        return self.db.execute_query(
            f"SELECT * FROM {self.table_name} WHERE {field} = ?",
            (value,)
        )
    
    def exists(self, id: int) -> bool:
        """Check if a record exists"""
        result = self.db.get_single_result(
            f"SELECT 1 FROM {self.table_name} WHERE {self.primary_key} = ?",
            (id,)
        )
        return bool(result)
    
    def count(self) -> int:
        """Get total count of records"""
        result = self.db.get_single_result(
            f"SELECT COUNT(*) as count FROM {self.table_name}"
        )
        return result['count'] if result else 0
    
    def search(self, query: str, fields: List[str]) -> List[Dict[str, Any]]:
        """Search records across specified fields"""
        conditions = " OR ".join([f"{field} LIKE ?" for field in fields])
        params = tuple(f"%{query}%" for _ in fields)
        return self.db.execute_query(
            f"SELECT * FROM {self.table_name} WHERE {conditions}",
            params
        ) 