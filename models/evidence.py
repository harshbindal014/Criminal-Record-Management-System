from typing import Dict, List, Optional, Any
from datetime import datetime
from .base_model import BaseModel
from utils.image_helper import ImageHelper
import os

class EvidenceModel(BaseModel):
    table_name = "evidence"
    
    def __init__(self):
        super().__init__()
        self.searchable_fields = ['name', 'type', 'status', 'description', 'notes']
    
    def create_with_image(self, data: Dict[str, Any], image_path: Optional[str] = None) -> int:
        """Create evidence record with optional image"""
        if image_path and os.path.exists(image_path):
            # Process and save the image
            saved_path = ImageHelper.save_image(
                image_path,
                'assets/images/evidence',
                'evidence'
            )
            if saved_path:
                data['image_path'] = saved_path
        
        # Add timestamp
        data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return self.create(data)
    
    def update_with_image(self, id: int, data: Dict[str, Any], new_image_path: Optional[str] = None) -> None:
        """Update evidence record with optional new image"""
        current_record = self.get_by_id(id)
        if not current_record:
            raise ValueError(f"Evidence with ID {id} not found")
        
        # Handle image update
        if new_image_path and os.path.exists(new_image_path):
            # Delete old image if it exists
            if current_record.get('image_path'):
                ImageHelper.delete_image(current_record['image_path'])
            
            # Save new image
            saved_path = ImageHelper.save_image(
                new_image_path,
                'assets/images/evidence',
                'evidence'
            )
            if saved_path:
                data['image_path'] = saved_path
        
        self.update(id, data)
    
    def delete_with_image(self, id: int) -> None:
        """Delete evidence record and associated image"""
        record = self.get_by_id(id)
        if record and record.get('image_path'):
            ImageHelper.delete_image(record['image_path'])
        self.delete(id)
    
    def get_by_case(self, case_id: int) -> List[Dict[str, Any]]:
        """Get all evidence for a specific case"""
        return self.get_by_field('case_id', case_id)
    
    def get_evidence_with_case_details(self, evidence_id: int) -> Optional[Dict[str, Any]]:
        """Get evidence with associated case details"""
        return self.db.get_single_result("""
            SELECT e.*, c.title as case_title, c.status as case_status
            FROM evidence e
            LEFT JOIN cases c ON e.case_id = c.id
            WHERE e.id = ?
        """, (evidence_id,))
    
    def get_recent_evidence(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recently added evidence"""
        return self.db.execute_query(
            f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
    
    def search_evidence(self, query: str) -> List[Dict[str, Any]]:
        """Search evidence across multiple fields"""
        return self.search(query, self.searchable_fields)
    
    def get_evidence_stats(self) -> Dict[str, Any]:
        """Get evidence statistics"""
        total = self.count()
        
        case_stats = self.db.execute_query("""
            SELECT c.title, COUNT(e.id) as evidence_count
            FROM cases c
            LEFT JOIN evidence e ON c.id = e.case_id
            GROUP BY c.id, c.title
            ORDER BY evidence_count DESC
            LIMIT 10
        """)
        
        monthly_stats = self.db.execute_query("""
            SELECT strftime('%Y-%m', date_collected) as month,
                   COUNT(*) as evidence_count
            FROM evidence
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        """)
        
        return {
            'total_evidence': total,
            'case_stats': case_stats,
            'monthly_stats': monthly_stats
        }
    
    def get_all_with_case_titles(self) -> List[Dict[str, Any]]:
        """Get all evidence records with their associated case titles"""
        return self.db.execute_query("""
            SELECT e.*, c.title as case_title
            FROM evidence e
            LEFT JOIN cases c ON e.case_id = c.id
            ORDER BY e.date_collected DESC
        """)
        
    def get_evidence_by_case(self, case_id: int) -> List[Dict[str, Any]]:
        """Get all evidence records for a specific case"""
        return self.db.execute_query("""
            SELECT e.*, c.title as case_title
            FROM evidence e
            LEFT JOIN cases c ON e.case_id = c.id
            WHERE e.case_id = ?
            ORDER BY e.date_collected DESC
        """, (case_id,))

    def get_evidence_report(self, start_date, end_date) -> List[Dict[str, Any]]:
        """Generate evidence report for the given date range"""
        return self.db.execute_query("""
            SELECT 
                e.id,
                e.evidence_number,
                e.type,
                e.description,
                e.date_collected,
                c.title as case_title,
                c.status as case_status,
                GROUP_CONCAT(DISTINCT cr.name) as related_criminals
            FROM evidence e
            LEFT JOIN cases c ON e.case_id = c.id
            LEFT JOIN case_criminals cc ON c.id = cc.case_id
            LEFT JOIN criminals cr ON cc.criminal_id = cr.id
            WHERE e.date_collected BETWEEN ? AND ?
            GROUP BY e.id
            ORDER BY e.date_collected DESC
        """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

    def get_statistics_report(self, start_date, end_date) -> List[Dict[str, Any]]:
        """Generate evidence statistics report for the given date range"""
        return self.db.execute_query("""
            SELECT 
                type,
                COUNT(*) as total_count,
                COUNT(DISTINCT case_id) as case_count
            FROM evidence
            WHERE date_collected BETWEEN ? AND ?
            GROUP BY type
            ORDER BY total_count DESC
        """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

    def get_inventory_report(self, start_date, end_date) -> List[Dict[str, Any]]:
        """Generate evidence inventory report for the given date range"""
        return self.db.execute_query("""
            SELECT 
                e.id,
                e.evidence_number,
                e.type,
                e.description,
                e.notes,
                e.date_collected,
                c.title as case_title,
                c.status as case_status
            FROM evidence e
            LEFT JOIN cases c ON e.case_id = c.id
            WHERE e.date_collected BETWEEN ? AND ?
            ORDER BY e.date_collected DESC
        """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

    def get_custody_report(self, start_date, end_date) -> List[Dict[str, Any]]:
        """Generate chain of custody report for the given date range"""
        return self.db.execute_query("""
            SELECT 
                e.id,
                e.evidence_number,
                e.type,
                e.date_collected,
                e.notes,
                c.title as case_title,
                GROUP_CONCAT(DISTINCT cr.name) as related_criminals
            FROM evidence e
            LEFT JOIN cases c ON e.case_id = c.id
            LEFT JOIN case_criminals cc ON c.id = cc.case_id
            LEFT JOIN criminals cr ON cc.criminal_id = cr.id
            WHERE e.date_collected BETWEEN ? AND ?
            GROUP BY e.id
            ORDER BY e.date_collected DESC
        """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))) 