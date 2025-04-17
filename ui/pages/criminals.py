from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFrame, QMessageBox, QDialog, QTableWidget,
                             QTableWidgetItem, QHeaderView, QComboBox, QLabel,
                             QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon
from ui.widgets.data_table import DataTable
from ui.widgets.form_widget import FormWidget
from models.criminal import CriminalModel
from datetime import datetime
from ui.dialogs.add_criminal import AddCriminalDialog

class CriminalDialog(QDialog):
    def __init__(self, parent=None, criminal_data=None):
        super().__init__(parent)
        self.criminal_data = criminal_data
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Criminal Record")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        
        # Create form
        fields = [
            {
                'name': 'name',
                'type': 'text',
                'label': 'Full Name',
                'required': True,
                'placeholder': 'Enter full name'
            },
            {
                'name': 'age',
                'type': 'number',
                'label': 'Age',
                'required': True,
                'min': 0,
                'max': 150
            },
            {
                'name': 'gender',
                'type': 'select',
                'label': 'Gender',
                'required': True,
                'options': ['Male', 'Female', 'Other']
            },
            {
                'name': 'crime_type',
                'type': 'select',
                'label': 'Crime Type',
                'required': True,
                'options': [
                    'Theft',
                    'Assault',
                    'Fraud',
                    'Drug Trafficking',
                    'Homicide',
                    'Cybercrime',
                    'Other'
                ]
            },
            {
                'name': 'arrest_date',
                'type': 'date',
                'label': 'Arrest Date',
                'required': True
            },
            {
                'name': 'status',
                'type': 'select',
                'label': 'Status',
                'required': True,
                'options': ['In Custody', 'Released', 'Wanted', 'Deceased']
            },
            {
                'name': 'image_path',
                'type': 'file',
                'label': 'Profile Image',
                'required': False,
                'file_types': 'Images (*.png *.jpg *.jpeg)'
            },
            {
                'name': 'notes',
                'type': 'textarea',
                'label': 'Notes',
                'required': False,
                'placeholder': 'Enter any additional notes'
            }
        ]
        
        self.form = FormWidget(fields)
        self.form.form_submitted.connect(self.handle_submit)
        self.form.form_cancelled.connect(self.reject)
        
        # Set data if editing
        if self.criminal_data:
            self.form.set_data(self.criminal_data)
        
        layout.addWidget(self.form)
        
    def handle_submit(self, data):
        """Handle form submission"""
        self.submitted_data = data
        self.accept()

class CriminalsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.criminal_model = CriminalModel()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Create top section with title and add button
        top_section = QFrame()
        top_section.setObjectName("top-section")
        top_layout = QHBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("Criminals")
        title.setObjectName("page-title")
        top_layout.addWidget(title)
        
        # Add spacer
        top_layout.addStretch()
        
        # Add Criminal button
        add_btn = QPushButton("Add Criminal")
        add_btn.setObjectName("primary-button")
        add_btn.clicked.connect(self.show_add_dialog)
        top_layout.addWidget(add_btn)
        
        layout.addWidget(top_section)
        
        # Create search section
        search_section = QFrame()
        search_section.setObjectName("search-section")
        search_layout = QHBoxLayout(search_section)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search criminals...")
        self.search_input.setObjectName("search-input")
        self.search_input.textChanged.connect(self.handle_search)
        search_layout.addWidget(self.search_input)
        
        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.setObjectName("filter-combo")
        self.filter_combo.addItems(["All", "Wanted", "Arrested", "In Custody"])
        self.filter_combo.currentTextChanged.connect(self.handle_filter)
        search_layout.addWidget(self.filter_combo)
        
        layout.addWidget(search_section)
        
        # Create table container
        table_container = QFrame()
        table_container.setObjectName("table-container")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        
        # Create table
        self.table = QTableWidget()
        self.table.setObjectName("criminals-table")
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Age", "Gender", "Crime Type", "Status", "Arrest Date"
        ])
        
        # Set table properties
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_container)
        
        # Create pagination section
        pagination = QFrame()
        pagination.setObjectName("pagination")
        pagination_layout = QHBoxLayout(pagination)
        pagination_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add spacer
        pagination_layout.addStretch()
        
        # Previous button
        prev_btn = QPushButton("Previous")
        prev_btn.setObjectName("pagination-button")
        pagination_layout.addWidget(prev_btn)
        
        # Next button
        next_btn = QPushButton("Next")
        next_btn.setObjectName("pagination-button")
        pagination_layout.addWidget(next_btn)
        
        layout.addWidget(pagination)
        
        # Set styling
        self.setStyleSheet("""
            QWidget {
                background: white;
                color: #202124;
            }
            #page-title {
                font-size: 24px;
                font-weight: bold;
                color: #202124;
                font-family: 'Segoe UI';
            }
            #primary-button {
                background: #1a73e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
            #primary-button:hover {
                background: #1557b0;
            }
            #search-input {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                color: #202124;
                background: white;
            }
            #search-input:focus {
                border-color: #1a73e8;
                outline: none;
            }
            #filter-combo {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 7px 12px;
                min-width: 120px;
                color: #202124;
                background: white;
            }
            #table-container {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 1px;
            }
            QTableWidget {
                border: none;
                gridline-color: #f1f3f4;
                background-color: white;
                color: #202124;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f1f3f4;
                color: #202124;
                background-color: white;
            }
            QTableWidget::item:selected {
                background: #e8f0fe;
                color: #202124;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
                color: #202124;
            }
            QHeaderView::section {
                background: #f8f9fa;
                color: #5f6368;
                font-weight: bold;
                padding: 12px;
                border: none;
                border-bottom: 1px solid #e0e0e0;
            }
            #pagination-button {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
                color: #202124;
            }
            #pagination-button:hover {
                background: #f8f9fa;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #5f6368;
                margin-top: 2px;
            }
        """)
        
        # Load initial data
        self.load_data()
        
    def load_data(self):
        """Load criminals data into table"""
        try:
            criminals = self.criminal_model.get_all()
            self.table.setRowCount(len(criminals))
            
            for row, criminal in enumerate(criminals):
                self.table.setItem(row, 0, QTableWidgetItem(str(criminal['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(criminal['name']))
                self.table.setItem(row, 2, QTableWidgetItem(str(criminal['age'])))
                self.table.setItem(row, 3, QTableWidgetItem(criminal['gender']))
                self.table.setItem(row, 4, QTableWidgetItem(criminal['crime_type']))
                self.table.setItem(row, 5, QTableWidgetItem(criminal['status']))
                self.table.setItem(row, 6, QTableWidgetItem(criminal['arrest_date']))
                
                # Set item properties
                for col in range(7):
                    item = self.table.item(row, col)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    
        except Exception as e:
            print(f"Error loading criminals: {str(e)}")
            
    def show_add_dialog(self):
        """Show add criminal dialog"""
        dialog = AddCriminalDialog(self)
        if dialog.exec_():
            self.load_data()
            
    def handle_search(self, text):
        """Handle search input changes"""
        try:
            text = text.lower().strip()
            if text:
                criminals = []
                all_criminals = self.criminal_model.get_all()
                for criminal in all_criminals:
                    # Search in multiple fields
                    if (text in str(criminal['id']).lower() or
                        text in criminal['name'].lower() or
                        text in str(criminal['age']).lower() or
                        text in criminal['gender'].lower() or
                        text in criminal['crime_type'].lower() or
                        text in criminal['status'].lower()):
                        criminals.append(criminal)
            else:
                criminals = self.criminal_model.get_all()
                
            self.update_table(criminals)
            
        except Exception as e:
            print(f"Error searching criminals: {str(e)}")
            
    def handle_filter(self, status):
        """Handle filter changes"""
        try:
            if status == "All":
                criminals = self.criminal_model.get_all()
            else:
                criminals = self.criminal_model.get_by_status(status)
                
            self.update_table(criminals)
            
        except Exception as e:
            print(f"Error filtering criminals: {str(e)}")
            
    def update_table(self, criminals):
        """Update table with filtered data"""
        self.table.setRowCount(len(criminals))
        
        for row, criminal in enumerate(criminals):
            self.table.setItem(row, 0, QTableWidgetItem(str(criminal['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(criminal['name']))
            self.table.setItem(row, 2, QTableWidgetItem(str(criminal['age'])))
            self.table.setItem(row, 3, QTableWidgetItem(criminal['gender']))
            self.table.setItem(row, 4, QTableWidgetItem(criminal['crime_type']))
            self.table.setItem(row, 5, QTableWidgetItem(criminal['status']))
            self.table.setItem(row, 6, QTableWidgetItem(criminal['arrest_date']))
            
            # Set item properties
            for col in range(7):
                item = self.table.item(row, col)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter) 