from typing import Dict, List, Optional, Any
from datetime import datetime
from .base_model import BaseModel
from utils.image_helper import ImageHelper
import os

class CriminalModel(BaseModel):
    table_name = "criminals"
    
    def __init__(self):
        super().__init__()
        self.searchable_fields = ['name', 'crime_type', 'status', 'notes']
        
    def create_with_image(self, data: Dict[str, Any], image_path: Optional[str] = None) -> int:
        """Create a criminal record with optional image"""
        if image_path and os.path.exists(image_path):
            # Process and save the image
            saved_path = ImageHelper.save_image(
                image_path,
                'assets/images/criminals',
                'criminal'
            )
            if saved_path:
                data['image_path'] = saved_path
        
        # Add timestamps
        data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data['updated_at'] = data['created_at']
        
        return self.create(data)
    
    def update_with_image(self, id: int, data: Dict[str, Any], new_image_path: Optional[str] = None) -> None:
        """Update a criminal record with optional new image"""
        current_record = self.get_by_id(id)
        if not current_record:
            raise ValueError(f"Criminal with ID {id} not found")
        
        # Handle image update
        if new_image_path and os.path.exists(new_image_path):
            # Delete old image if it exists
            if current_record.get('image_path'):
                ImageHelper.delete_image(current_record['image_path'])
            
            # Save new image
            saved_path = ImageHelper.save_image(
                new_image_path,
                'assets/images/criminals',
                'criminal'
            )
            if saved_path:
                data['image_path'] = saved_path
        
        # Update timestamp
        data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.update(id, data)
    
    def delete_with_image(self, id: int) -> None:
        """Delete a criminal record and associated image"""
        record = self.get_by_id(id)
        if record and record.get('image_path'):
            ImageHelper.delete_image(record['image_path'])
        self.delete(id)
    
    def search_criminals(self, query: str) -> List[Dict[str, Any]]:
        """Search criminals across multiple fields"""
        return self.search(query, self.searchable_fields)
    
    def get_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get criminals by status"""
        return self.get_by_field('status', status)
    
    def get_by_crime_type(self, crime_type: str) -> List[Dict[str, Any]]:
        """Get criminals by crime type"""
        return self.get_by_field('crime_type', crime_type)
    
    def get_recent_criminals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recently added criminals"""
        return self.db.execute_query(
            f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
    
    def get_crime_type_stats(self) -> List[Dict[str, Any]]:
        """Get statistics of criminals by crime type"""
        return self.db.execute_query("""
            SELECT crime_type, COUNT(*) as count
            FROM criminals
            GROUP BY crime_type
            ORDER BY count DESC
        """)

    def get_statistics_report(self, start_date, end_date) -> List[Dict[str, Any]]:
        """Generate criminal statistics report for the given date range"""
        return self.db.execute_query("""
            SELECT 
                crime_type,
                COUNT(*) as total_count,
                SUM(CASE WHEN status = 'Arrested' THEN 1 ELSE 0 END) as arrested_count,
                SUM(CASE WHEN status = 'Wanted' THEN 1 ELSE 0 END) as wanted_count,
                SUM(CASE WHEN status = 'In Custody' THEN 1 ELSE 0 END) as in_custody_count,
                AVG(age) as average_age,
                SUM(CASE WHEN gender = 'Male' THEN 1 ELSE 0 END) as male_count,
                SUM(CASE WHEN gender = 'Female' THEN 1 ELSE 0 END) as female_count
            FROM criminals
            WHERE arrest_date BETWEEN ? AND ?
            GROUP BY crime_type
            ORDER BY total_count DESC
        """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

    def get_history_report(self, start_date, end_date) -> List[Dict[str, Any]]:
        """Generate criminal history report for the given date range"""
        return self.db.execute_query("""
            SELECT 
                cr.id,
                cr.name,
                cr.age,
                cr.gender,
                cr.crime_type,
                cr.status,
                cr.arrest_date,
                COUNT(DISTINCT cc.case_id) as case_count,
                GROUP_CONCAT(DISTINCT c.title) as cases,
                (
                    SELECT COUNT(*)
                    FROM case_criminals cc2
                    JOIN cases c2 ON cc2.case_id = c2.id
                    WHERE cc2.criminal_id = cr.id AND c2.status = 'Closed'
                ) as closed_cases
            FROM criminals cr
            LEFT JOIN case_criminals cc ON cr.id = cc.criminal_id
            LEFT JOIN cases c ON cc.case_id = c.id
            WHERE cr.arrest_date BETWEEN ? AND ?
            GROUP BY cr.id
            ORDER BY cr.arrest_date DESC
        """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

    def get_total_count(self) -> int:
        """Get total number of criminals"""
        try:
            result = self.db.execute_query(
                f"SELECT COUNT(*) as count FROM {self.table_name}"
            )
            return result[0]['count'] if result else 0
        except Exception as e:
            print(f"Error getting total count: {str(e)}")
            return 0

    def get_criminal(self, criminal_id):
        """Get a criminal by ID."""
        try:
            query = "SELECT * FROM criminals WHERE id = ?"
            self.cursor.execute(query, (criminal_id,))
            criminal = self.cursor.fetchone()
            if not criminal:
                raise ValueError(f"Criminal with ID {criminal_id} does not exist")
            return criminal
        except Exception as e:
            print(f"Error getting criminal: {str(e)}")
            raise ValueError(f"Criminal with ID {criminal_id} does not exist") 