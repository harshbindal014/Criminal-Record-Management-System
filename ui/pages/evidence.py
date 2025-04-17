from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFrame, QMessageBox, QDialog, QComboBox,
                             QLabel, QFileDialog, QLineEdit, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from ui.widgets.data_table import DataTable
from ui.widgets.form_widget import FormWidget
from models.evidence import EvidenceModel
from models.case import CaseModel
from utils.image_helper import save_image, get_image_path
from datetime import datetime
from ui.dialogs.evidence_dialog import EvidenceDialog

class EvidenceDialog(QDialog):
    def __init__(self, parent=None, evidence_data=None):
        super().__init__(parent)
        self.evidence_data = evidence_data
        self.evidence_model = EvidenceModel()
        self.case_model = CaseModel()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Evidence Record")
        self.setMinimumWidth(700)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Get cases for linking
        cases = self.case_model.get_all()
        case_options = [{'label': f"{case['title']} (ID: {case['id']})", 
                        'value': case['id']} for case in cases]
        
        # Create form
        fields = [
            {
                'name': 'case_id',
                'type': 'select',
                'label': 'Related Case',
                'required': True,
                'options': case_options
            },
            {
                'name': 'name',
                'type': 'text',
                'label': 'Evidence Name',
                'required': True,
                'placeholder': 'Enter evidence name'
            },
            {
                'name': 'type',
                'type': 'select',
                'label': 'Evidence Type',
                'required': True,
                'options': [
                    'Physical',
                    'Digital',
                    'Documentary',
                    'Biological',
                    'Trace',
                    'Other'
                ]
            },
            {
                'name': 'status',
                'type': 'select',
                'label': 'Status',
                'required': True,
                'options': [
                    'In Storage',
                    'In Analysis',
                    'Returned',
                    'Destroyed',
                    'Missing'
                ]
            },
            {
                'name': 'collection_date',
                'type': 'date',
                'label': 'Collection Date',
                'required': True
            },
            {
                'name': 'collection_location',
                'type': 'text',
                'label': 'Collection Location',
                'required': True,
                'placeholder': 'Enter location where evidence was collected'
            },
            {
                'name': 'storage_location',
                'type': 'text',
                'label': 'Storage Location',
                'required': True,
                'placeholder': 'Enter evidence storage location'
            },
            {
                'name': 'image_path',
                'type': 'file',
                'label': 'Evidence Image',
                'required': False,
                'file_types': 'Images (*.png *.jpg *.jpeg)'
            },
            {
                'name': 'description',
                'type': 'textarea',
                'label': 'Description',
                'required': True,
                'placeholder': 'Enter evidence description'
            },
            {
                'name': 'notes',
                'type': 'textarea',
                'label': 'Additional Notes',
                'required': False,
                'placeholder': 'Enter any additional notes'
            }
        ]
        
        self.form = FormWidget(fields)
        self.form.form_submitted.connect(self.handle_submit)
        self.form.form_cancelled.connect(self.reject)
        
        # Set data if editing
        if self.evidence_data:
            self.form.set_data(self.evidence_data)
        
        layout.addWidget(self.form)
    
    def handle_submit(self, data):
        """Handle form submission"""
        self.submitted_data = data
        self.accept()

class EvidencePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.evidence_model = EvidenceModel()
        self.case_model = CaseModel()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Top section with title and add button
        top_section = QFrame()
        top_section.setObjectName("top-section")
        top_layout = QHBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Evidence")
        title.setObjectName("page-title")
        top_layout.addWidget(title)
        
        top_layout.addStretch()
        
        add_btn = QPushButton("Add Evidence")
        add_btn.setObjectName("primary-button")
        add_btn.clicked.connect(self.handle_add)
        top_layout.addWidget(add_btn)
        
        layout.addWidget(top_section)
        
        # Evidence table
        columns = [
            {'key': 'id', 'title': 'ID'},
            {'key': 'name', 'title': 'Name'},
            {'key': 'type', 'title': 'Type'},
            {'key': 'storage_location', 'title': 'Storage Location'},
            {'key': 'status', 'title': 'Status'},
            {'key': 'case_id', 'title': 'Case ID'}
        ]
        self.table = DataTable(columns, page_size=10)
        self.table.row_double_clicked.connect(self.handle_row_click)
        layout.addWidget(self.table)
        
        self.setStyleSheet("""
            QWidget {
                background: white;
                color: #202124;
            }
            #top-section {
                background: transparent;
            }
            #page-title {
                font-size: 24px;
                font-weight: bold;
                color: #202124;
            }
            #primary-button {
                background: #1a73e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                min-width: 120px;
                min-height: 36px;
            }
            #primary-button:hover {
                background: #1557b0;
            }
        """)
        
        self.refresh()
        
    def refresh(self):
        """Refresh the table data"""
        try:
            evidence_list = self.evidence_model.get_all()
            self.table.set_data(evidence_list)
        except Exception as e:
            print(f"Error refreshing evidence: {str(e)}")
            
    def handle_add(self):
        """Handle add button click"""
        dialog = EvidenceDialog(self)
        if dialog.exec_() == EvidenceDialog.Accepted:
            try:
                self.evidence_model.create(dialog.submitted_data)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create evidence record: {str(e)}")
                
    def handle_row_click(self, row_data):
        """Handle row double click"""
        evidence_id = row_data['id']
        evidence_data = self.evidence_model.get_by_id(evidence_id)
        
        dialog = EvidenceDialog(self, evidence_data)
        if dialog.exec_() == EvidenceDialog.Accepted:
            try:
                self.evidence_model.update(evidence_id, dialog.submitted_data)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update evidence record: {str(e)}") 