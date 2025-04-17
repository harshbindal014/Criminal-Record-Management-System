from typing import Dict, List, Optional, Any
from datetime import datetime
from .base_model import BaseModel
import sqlite3

class CaseModel(BaseModel):
    table_name = "cases"
    
    def __init__(self):
        """Initialize the case model"""
        super().__init__()
        self.searchable_fields = ['title', 'status', 'description']
    
    def create_case(self, data: Dict[str, Any], criminal_ids: List[int] = None) -> int:
        """Create a new case with optional linked criminals"""
        # Add timestamps
        data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data['updated_at'] = data['created_at']
        
        # Create case
        case_id = self.create(data)
        
        # Link criminals if provided
        if criminal_ids:
            self.link_criminals(case_id, criminal_ids)
            
        return case_id
    
    def update_case(self, id: int, data: Dict[str, Any], criminal_ids: List[int] = None) -> None:
        """Update a case with optional criminal links update"""
        if not self.exists(id):
            raise ValueError(f"Case with ID {id} not found")
        
        # Update timestamp
        data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update case
        self.update(id, data)
        
        # Update criminal links if provided
        if criminal_ids is not None:  # Allow empty list to remove all links
            self.update_criminal_links(id, criminal_ids)
    
    def link_criminals(self, case_id: int, criminal_ids: List[int]) -> None:
        """Link criminals to a case"""
        # First verify all criminals exist
        for criminal_id in criminal_ids:
            result = self.db.get_single_result(
                "SELECT id FROM criminals WHERE id = ?",
                (criminal_id,)
            )
            if not result:
                raise ValueError(f"Criminal ID {criminal_id} does not exist")
        
        # If all criminals exist, create the links
        values = [(case_id, criminal_id) for criminal_id in criminal_ids]
        self.db.execute_many(
            "INSERT INTO case_criminals (case_id, criminal_id) VALUES (?, ?)",
            values
        )
    
    def update_criminal_links(self, case_id: int, criminal_ids: List[int]) -> None:
        """Update the criminals linked to a case"""
        # Remove existing links
        self.db.execute_query(
            "DELETE FROM case_criminals WHERE case_id = ?",
            (case_id,)
        )
        
        # Add new links
        if criminal_ids:
            self.link_criminals(case_id, criminal_ids)
    
    def get_case_criminals(self, case_id: int) -> List[Dict[str, Any]]:
        """Get all criminals linked to a case"""
        return self.db.execute_query("""
            SELECT c.*
            FROM criminals c
            JOIN case_criminals cc ON c.id = cc.criminal_id
            WHERE cc.case_id = ?
        """, (case_id,))
    
    def get_case_with_details(self, case_id: int) -> Optional[Dict[str, Any]]:
        """Get case with criminal details"""
        case = self.db.get_single_result("""
            SELECT c.*
            FROM cases c
            WHERE c.id = ?
        """, (case_id,))
        
        if case:
            case['criminals'] = self.get_case_criminals(case_id)
        
        return case
    
    def get_cases_by_officer(self, officer_id: int) -> List[Dict[str, Any]]:
        """Get all cases assigned to an officer"""
        return self.get_by_field('officer_id', officer_id)
    
    def get_cases_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get cases by status"""
        return self.get_by_field('status', status)
    
    def get_recent_cases(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recently created cases"""
        return self.db.execute_query(
            f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
    
    def get_case_stats(self) -> Dict[str, Any]:
        """Get case statistics"""
        total = self.count()
        
        status_stats = self.db.execute_query("""
            SELECT status, COUNT(*) as count
            FROM cases
            GROUP BY status
        """)
        
        monthly_stats = self.db.execute_query("""
            SELECT 
                strftime('%Y-%m', date_reported) as month,
                COUNT(*) as total_cases,
                SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) as closed_cases
            FROM cases
            GROUP BY month
            ORDER BY month ASC
        """)
        
        return {
            'total_cases': total,
            'status_stats': status_stats,
            'monthly_stats': monthly_stats
        }
    
    def search_cases(self, query: str) -> List[Dict[str, Any]]:
        """Search cases across multiple fields"""
        return self.search(query, self.searchable_fields)
    
    def get_all_cases(self) -> List[Dict[str, Any]]:
        """Get all cases"""
        return self.db.execute_query("""
            SELECT c.*
            FROM cases c
            ORDER BY c.date_reported DESC
        """)

    def get_status_report(self, start_date, end_date) -> List[Dict[str, Any]]:
        """Generate case status report for the given date range"""
        return self.db.execute_query("""
            SELECT 
                c.id,
                c.title,
                c.status,
                c.date_reported,
                c.closed_date,
                (SELECT COUNT(*) FROM case_criminals cc WHERE cc.case_id = c.id) as criminal_count,
                (SELECT COUNT(*) FROM evidence e WHERE e.case_id = c.id) as evidence_count
            FROM cases c
            WHERE c.date_reported BETWEEN ? AND ?
            ORDER BY c.date_reported DESC
        """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

    def get_timeline_report(self, start_date, end_date) -> List[Dict[str, Any]]:
        """Generate case timeline report for the given date range"""
        return self.db.execute_query("""
            SELECT 
                c.id,
                c.title,
                c.description,
                c.status,
                c.date_reported,
                c.closed_date,
                GROUP_CONCAT(cr.name, ', ') as criminals,
                (
                    SELECT GROUP_CONCAT(e.description || ' (' || e.type || ')', ', ')
                    FROM evidence e
                    WHERE e.case_id = c.id
                ) as evidence
            FROM cases c
            LEFT JOIN case_criminals cc ON c.id = cc.case_id
            LEFT JOIN criminals cr ON cc.criminal_id = cr.id
            WHERE c.date_reported BETWEEN ? AND ?
            GROUP BY c.id
            ORDER BY c.date_reported DESC
        """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

    def get_monthly_case_trends(self, start_date=None, end_date=None):
        """Get monthly case counts for a date range
        
        Args:
            start_date (datetime, optional): Start date for trends. Defaults to 12 months ago.
            end_date (datetime, optional): End date for trends. Defaults to current date.
        """
        try:
            if start_date is None:
                start_date_clause = "date('now', '-12 months')"
            else:
                start_date_clause = f"date('{start_date.strftime('%Y-%m-%d')}')"
                
            if end_date is None:
                end_date_clause = "date('now')"
            else:
                end_date_clause = f"date('{end_date.strftime('%Y-%m-%d')}')"
            
            query = f"""
                SELECT 
                    strftime('%Y-%m', date_reported) as month,
                    COUNT(*) as count
                FROM cases 
                WHERE date_reported >= {start_date_clause}
                AND date_reported <= {end_date_clause}
                GROUP BY strftime('%Y-%m', date_reported)
                ORDER BY month ASC
            """
            
            results = self.db.execute_query(query)
            return [{'month': dict(row)['month'], 'count': dict(row)['count']} for row in results]
        except Exception as e:
            print(f"Error getting monthly case trends: {str(e)}")
            return []

    def count_by_status(self, status: str) -> int:
        """Count cases by status"""
        result = self.db.get_single_result(
            "SELECT COUNT(*) as count FROM cases WHERE status = ?",
            (status,)
        )
        return result['count'] if result else 0

    def get_monthly_case_counts(self, start_date: str, end_date: str) -> List[tuple]:
        """Get monthly case counts for the specified date range"""
        return self.db.execute_query("""
            WITH RECURSIVE dates(date) AS (
                SELECT date(?)
                UNION ALL
                SELECT date(date, '+1 month')
                FROM dates
                WHERE date < date(?)
            )
            SELECT 
                strftime('%Y-%m', dates.date) as month,
                COUNT(cases.id) as count
            FROM dates
            LEFT JOIN cases ON strftime('%Y-%m', cases.date_reported) = strftime('%Y-%m', dates.date)
            GROUP BY strftime('%Y-%m', dates.date)
            ORDER BY dates.date ASC
        """, (start_date, end_date)) 