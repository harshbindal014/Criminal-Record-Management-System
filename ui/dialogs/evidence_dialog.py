from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                            QGroupBox, QScrollArea, QWidget, QLabel, QLineEdit,
                            QMessageBox)
from PyQt5.QtCore import Qt
from ui.widgets.form_widget import FormWidget
from models.evidence import EvidenceModel
from models.case import CaseModel

class EvidenceDialog(QDialog):
    def __init__(self, parent=None, evidence_data=None, case_id=None):
        super().__init__(parent)
        self.evidence_data = evidence_data
        self.case_id = case_id
        self.evidence_model = EvidenceModel()
        self.case_model = CaseModel()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Evidence Record")
        self.setFixedWidth(800)
        self.setFixedHeight(600)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Create horizontal layout for two columns
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)
        
        # Left section - Evidence Details
        left_section = QWidget()
        left_layout = QVBoxLayout(left_section)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        details_label = QLabel("Evidence Details")
        details_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 16px;")
        left_layout.addWidget(details_label)
        
        # Create scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        # Form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Form fields
        fields = [
            {
                'name': 'related_case',
                'type': 'select',
                'label': 'Related Case *',
                'required': True,
                'options': self.get_case_options()
            },
            {
                'name': 'name',
                'type': 'text',
                'label': 'Evidence Name *',
                'required': True,
                'placeholder': 'Enter evidence name'
            },
            {
                'name': 'type',
                'type': 'select',
                'label': 'Evidence Type *',
                'required': True,
                'options': [
                    'Physical',
                    'Digital',
                    'Documentary',
                    'Biological',
                    'Other'
                ]
            },
            {
                'name': 'status',
                'type': 'select',
                'label': 'Status *',
                'required': True,
                'options': [
                    'In Storage',
                    'In Analysis',
                    'Returned',
                    'Destroyed'
                ]
            },
            {
                'name': 'collection_date',
                'type': 'date',
                'label': 'Collection Date *',
                'required': True
            },
            {
                'name': 'collection_location',
                'type': 'text',
                'label': 'Collection Location *',
                'required': True,
                'placeholder': 'Enter collection location'
            },
            {
                'name': 'storage_location',
                'type': 'text',
                'label': 'Storage Location *',
                'required': True,
                'placeholder': 'Enter storage location'
            },
            {
                'name': 'description',
                'type': 'textarea',
                'label': 'Description *',
                'required': True,
                'placeholder': 'Enter evidence description'
            }
        ]
        
        # Create form
        self.form = FormWidget(fields)
        form_layout.addWidget(self.form)
        
        scroll.setWidget(form_container)
        left_layout.addWidget(scroll)
        
        # Right section - Additional Information
        right_section = QWidget()
        right_layout = QVBoxLayout(right_section)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        info_label = QLabel("Additional Information")
        info_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 16px;")
        right_layout.addWidget(info_label)
        
        # Add sections to main horizontal layout
        content_layout.addWidget(left_section, 60)  # 60% width
        content_layout.addWidget(right_section, 40)  # 40% width
        
        # Add content layout to main layout
        layout.addLayout(content_layout)
        
        # Buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 8, 0, 0)
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary-button")
        cancel_btn.clicked.connect(self.reject)
        
        submit_btn = QPushButton("Submit")
        submit_btn.setObjectName("primary-button")
        submit_btn.clicked.connect(self.handle_submit)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(submit_btn)
        layout.addWidget(button_container)
        
        # Set dialog styling
        self.setStyleSheet("""
            QDialog {
                background: white;
            }
            QLabel {
                color: #202124;
                font-weight: 500;
                font-size: 12px;  # Larger, matching case dialog
                margin-bottom: 4px;
            }
            QLineEdit, QComboBox, QTextEdit, QDateEdit {
                border: 1px solid #dadce0;
                border-radius: 4px;
                padding: 6px 8px;  # More padding like case dialog
                background: white;
                color: #202124;
                font-size: 12px;  # Larger, matching case dialog
                min-height: 32px;  # Taller like case dialog
            }
            QTextEdit {
                min-height: 64px;  # Taller textarea like case dialog
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus {
                border: 1px solid #1a73e8;
                outline: none;
            }
            QPushButton {
                padding: 8px 16px;  # More padding like case dialog
                border-radius: 4px;
                font-size: 12px;  # Larger font like case dialog
                font-weight: 500;
                min-width: 80px;  # Wider like case dialog
                min-height: 32px;  # Taller like case dialog
            }
            QPushButton#primary-button {
                background: #1a73e8;
                color: white;
                border: none;
            }
            QPushButton#primary-button:hover {
                background: #1557b0;
            }
            QPushButton#secondary-button {
                background: white;
                color: #1a73e8;
                border: 1px solid #1a73e8;
            }
            QPushButton#secondary-button:hover {
                background: #f6fafe;
            }
            QComboBox::drop-down {
                border: none;
                width: 14px;  /* Smaller width */
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 3px solid #5f6368;
                margin-top: 1px;
            }
            QDateEdit::drop-down {
                border: none;
                width: 14px;  /* Smaller width */
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 3px solid #5f6368;
                margin-top: 1px;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f3f4;
                width: 4px;  /* Thinner scrollbar */
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #dadce0;
                min-height: 16px;
                border-radius: 2px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
                background: none;
            }
        """)
        
        # Load initial data if editing
        if self.evidence_data:
            self.form.set_data(self.evidence_data)
            
    def get_case_options(self):
        """Get list of cases for dropdown"""
        cases = self.case_model.get_all()
        return [f"Case-{case['id']}: {case['title']}" for case in cases]
            
    def handle_submit(self):
        """Handle form submission"""
        if self.form.validate():
            try:
                self.submitted_data = self.form.get_data()
                if self.case_id:
                    self.submitted_data['case_id'] = self.case_id
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e)) 