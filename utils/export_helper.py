from typing import List, Dict, Any
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
from datetime import datetime

class ExportHelper:
    @staticmethod
    def export_to_excel(data: List[Dict[str, Any]], file_path: str) -> str:
        """Export data to Excel file"""
        if not data:
            raise ValueError("No data to export")
            
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Export to Excel
        df.to_excel(file_path, index=False, engine='openpyxl')
        return file_path
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str) -> str:
        """Export data to CSV file"""
        if not data:
            raise ValueError("No data to export")
            
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Ensure export directory exists
        export_dir = 'exports'
        os.makedirs(export_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(export_dir, f"{filename}_{timestamp}.csv")
        
        # Export to CSV
        df.to_csv(file_path, index=False)
        return file_path
    
    @staticmethod
    def export_to_pdf(data: List[Dict[str, Any]], file_path: str, title: str) -> str:
        """Export data to PDF file"""
        if not data:
            raise ValueError("No data to export")
            
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        
        # Create story (content)
        story = []
        
        # Add title
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
        
        # Prepare table data
        if data:
            headers = list(data[0].keys())
            table_data = [headers]
            for item in data:
                row = [str(item.get(col, '')) for col in headers]
                table_data.append(row)
            
            # Create table
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            story.append(table)
        
        # Build PDF
        doc.build(story)
        return file_path
    
    @staticmethod
    def generate_case_report(case_data: Dict[str, Any], evidence_list: List[Dict[str, Any]],
                           criminal_list: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive case report in PDF format"""
        # Ensure export directory exists
        export_dir = 'exports'
        os.makedirs(export_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(export_dir, f"case_report_{case_data['id']}_{timestamp}.pdf")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=12
        )
        
        # Create story (content)
        story = []
        
        # Add title
        story.append(Paragraph(f"Case Report: {case_data['title']}", title_style))
        story.append(Spacer(1, 12))
        
        # Add case details
        story.append(Paragraph("Case Details", heading_style))
        case_details = [
            ["Case ID:", str(case_data['id'])],
            ["Status:", case_data['status']],
            ["Officer:", case_data.get('officer_name', 'Not Assigned')],
            ["Opened Date:", case_data['opened_date']],
            ["Closed Date:", case_data.get('closed_date', 'Not Closed')]
        ]
        
        case_table = Table(case_details)
        case_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
        ]))
        story.append(case_table)
        story.append(Spacer(1, 20))
        
        # Add criminals section
        if criminal_list:
            story.append(Paragraph("Linked Criminals", heading_style))
            criminal_data = [[
                "ID", "Name", "Age", "Crime Type", "Status"
            ]]
            for criminal in criminal_list:
                criminal_data.append([
                    str(criminal['id']),
                    criminal['name'],
                    str(criminal['age']),
                    criminal['crime_type'],
                    criminal['status']
                ])
            
            criminal_table = Table(criminal_data, repeatRows=1)
            criminal_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            story.append(criminal_table)
            story.append(Spacer(1, 20))
        
        # Add evidence section
        if evidence_list:
            story.append(Paragraph("Evidence List", heading_style))
            evidence_data = [[
                "ID", "Description", "Collection Date"
            ]]
            for evidence in evidence_list:
                evidence_data.append([
                    str(evidence['id']),
                    evidence['description'],
                    evidence['collected_on']
                ])
            
            evidence_table = Table(evidence_data, repeatRows=1)
            evidence_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            story.append(evidence_table)
        
        # Build PDF
        doc.build(story)
        return file_path

# Module-level functions that use the ExportHelper class
def export_to_excel(data: List[Dict[str, Any]], file_path: str) -> str:
    """Export data to Excel using the ExportHelper class"""
    return ExportHelper.export_to_excel(data, file_path)

def export_to_csv(data: List[Dict[str, Any]], filename: str) -> str:
    """Export data to CSV using the ExportHelper class"""
    return ExportHelper.export_to_csv(data, filename)

def export_to_pdf(data: List[Dict[str, Any]], file_path: str, title: str) -> str:
    """Export data to PDF using the ExportHelper class"""
    return ExportHelper.export_to_pdf(data, file_path, title)

def generate_case_report(case_data: Dict[str, Any], evidence_list: List[Dict[str, Any]],
                        criminal_list: List[Dict[str, Any]]) -> str:
    """Generate a case report using the ExportHelper class"""
    return ExportHelper.generate_case_report(case_data, evidence_list, criminal_list) 