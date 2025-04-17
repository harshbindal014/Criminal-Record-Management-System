from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFrame, QMessageBox, QDialog, QListWidget,
                             QListWidgetItem, QLabel, QLineEdit, QComboBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt
from ui.widgets.data_table import DataTable
from ui.widgets.form_widget import FormWidget
from models.case import CaseModel
from models.criminal import CriminalModel
from models.evidence import EvidenceModel
from models.user import UserModel
from datetime import datetime

class CaseDialog(QDialog):
    def __init__(self, parent=None, case_data=None):
        super().__init__(parent)
        self.case_data = case_data
        self.case_model = CaseModel()
        self.criminal_model = CriminalModel()
        self.user_model = UserModel()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Case Record")
        self.setMinimumWidth(1200)
        self.setMinimumHeight(900)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Create main form
        main_layout = QHBoxLayout()
        main_layout.setSpacing(24)
        
        # Left side - Case details (65% of width)
        details_container = QWidget()
        details_container.setMinimumWidth(750)
        details_layout = QVBoxLayout(details_container)
        details_layout.setContentsMargins(0, 0, 0, 0)
        
        details_group = QGroupBox("Case Details")
        form_layout = QVBoxLayout(details_group)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(24, 32, 24, 24)
        
        # Create scroll area for form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f3f4;
                width: 8px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #dadce0;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #bdc1c6;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Create form container
        form_container = QWidget()
        form_container_layout = QVBoxLayout(form_container)
        form_container_layout.setContentsMargins(0, 0, 0, 0)
        form_container_layout.setSpacing(20)
        
        fields = [
            {
                'name': 'case_number',
                'type': 'text',
                'label': 'Case Number',
                'required': True,
                'placeholder': 'Enter case number'
            },
            {
                'name': 'title',
                'type': 'text',
                'label': 'Case Title',
                'required': True,
                'placeholder': 'Enter case title'
            },
            {
                'name': 'status',
                'type': 'select',
                'label': 'Status',
                'required': True,
                'options': [
                    'Open',
                    'Under Investigation',
                    'Pending',
                    'Closed',
                    'Cold Case'
                ]
            },
            {
                'name': 'date_reported',
                'type': 'date',
                'label': 'Date Reported',
                'required': True
            },
            {
                'name': 'closed_date',
                'type': 'date',
                'label': 'Closed Date',
                'required': False
            },
            {
                'name': 'description',
                'type': 'textarea',
                'label': 'Description',
                'required': True,
                'placeholder': 'Enter detailed case description'
            }
        ]
        
        self.form = FormWidget(fields)
        self.form.setContentsMargins(0, 0, 0, 0)
        
        # Update form widget styles with improved field sizes
        self.form.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }
            .form-field {
                margin-bottom: 24px;
                min-height: 85px;
            }
            QLabel {
                color: #202124;
                font-weight: 500;
                margin-bottom: 8px;
                font-size: 14px;
            }
            QLineEdit, QComboBox, QDateEdit {
                min-height: 40px;
                padding: 8px 12px;
                border: 1px solid #dadce0;
                border-radius: 4px;
                background-color: white;
                color: #202124;
            }
            QTextEdit {
                min-height: 150px;  /* Increased height for description */
                padding: 12px;
                border: 1px solid #dadce0;
                border-radius: 4px;
                background-color: white;
                color: #202124;
                margin-bottom: 16px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #1a73e8;
                outline: none;
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
                margin-right: 8px;
            }
            QDateEdit::drop-down {
                border: none;
                width: 20px;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #5f6368;
                margin-right: 8px;
            }
        """)
        form_container_layout.addWidget(self.form)
        
        form_container_layout.addStretch()
        
        # Set form container as scroll area widget
        scroll_area.setWidget(form_container)
        form_layout.addWidget(scroll_area)
        
        details_layout.addWidget(details_group)
        
        # Right side - Linked Criminals (35% of width)
        criminals_group = QGroupBox("Linked Criminals")
        criminals_group.setMinimumWidth(350)
        criminals_layout = QVBoxLayout(criminals_group)
        criminals_layout.setSpacing(16)
        criminals_layout.setContentsMargins(20, 24, 20, 20)
        
        # Search box for criminals
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)
        search_label = QLabel("Search Criminals:")
        search_label.setStyleSheet("color: #202124; font-weight: 500;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter name to search...")
        self.search_input.setMinimumHeight(36)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        criminals_layout.addLayout(search_layout)
        
        # Criminals list with improved visibility
        self.criminals_list = QListWidget()
        self.criminals_list.setMinimumHeight(500)
        self.criminals_list.setSelectionMode(QListWidget.MultiSelection)
        criminals_layout.addWidget(self.criminals_list)
        
        # Update main layout proportions
        main_layout.addWidget(details_container, 65)
        main_layout.addWidget(criminals_group, 35)
        layout.addLayout(main_layout)
        
        # Button container with improved alignment
        button_container = QFrame()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 20, 0, 0)
        button_layout.setSpacing(16)
        button_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary-button")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Submit button
        submit_btn = QPushButton("Submit")
        submit_btn.setObjectName("primary-button")
        submit_btn.clicked.connect(self.handle_submit)
        button_layout.addWidget(submit_btn)
        
        layout.addWidget(button_container)
        
        # Update styles
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QGroupBox {
                font-size: 16px;
                font-weight: 500;
                margin-top: 1.5em;
                border: 1px solid #dadce0;
                border-radius: 8px;
                background-color: white;
                padding: 24px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 12px;
                color: #202124;
                background-color: white;
            }
            QListWidget {
                border: 1px solid #dadce0;
                border-radius: 4px;
                background-color: white;
                padding: 8px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f1f3f4;
                margin-bottom: 4px;
                color: #202124;
                font-weight: normal;
            }
            QListWidget::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
                border-radius: 4px;
                font-weight: 500;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
                border-radius: 4px;
            }
            QPushButton {
                padding: 8px 24px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: 500;
                min-width: 120px;
                min-height: 40px;
            }
            QPushButton#primary-button {
                background-color: #1a73e8;
                color: white;
                border: none;
            }
            QPushButton#primary-button:hover {
                background-color: #1557b0;
            }
            QPushButton#secondary-button {
                background-color: #ffffff;
                color: #1a73e8;
                border: 1px solid #1a73e8;
            }
            QPushButton#secondary-button:hover {
                background-color: #f6fafe;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                border: 1px solid #dadce0;
                border-radius: 4px;
                padding: 12px;
                font-size: 14px;
                color: #202124;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #1a73e8;
                outline: none;
            }
            QLabel {
                color: #202124;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        
        # Load criminals list with improved formatting
        criminals = self.criminal_model.get_all()
        for criminal in criminals:
            item = QListWidgetItem(f"{criminal['name']} (ID: {criminal['id']})")
            item.setData(Qt.UserRole, criminal['id'])
            item.setForeground(Qt.black)  # Set text color explicitly
            self.criminals_list.addItem(item)
        
        # Load initial data
        if self.case_data:
            # Get case details including criminals
            case_details = self.case_model.get_case_with_details(self.case_data['id'])
            self.form.set_data(case_details)
            
            # Select linked criminals
            if 'criminals' in case_details:
                for i in range(self.criminals_list.count()):
                    item = self.criminals_list.item(i)
                    criminal_id = item.data(Qt.UserRole)
                    if any(c['id'] == criminal_id for c in case_details['criminals']):
                        item.setSelected(True)
                        item.setBackground(Qt.lightGray)  # Highlight selected criminals
        
    def handle_submit(self):
        """Handle form submission"""
        if self.form.validate():
            try:
                # Get form data and selected criminals
                self.submitted_data = self.form.get_data()
                self.submitted_criminal_ids = self.get_selected_criminals()
                
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
    
    def get_selected_criminals(self):
        """Get list of selected criminal IDs"""
        return [
            self.criminals_list.item(i).data(Qt.UserRole)
            for i in range(self.criminals_list.count())
            if self.criminals_list.item(i).isSelected()
        ]

class CasesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.case_model = CaseModel()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create top section with title and add button
        top_section = QFrame()
        top_section.setObjectName("top-section")
        top_layout = QHBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("Cases")
        title.setObjectName("page-title")
        top_layout.addWidget(title)
        
        # Add spacer
        top_layout.addStretch()
        
        # Add Case button
        add_btn = QPushButton("Add Case")
        add_btn.setObjectName("primary-button")
        add_btn.clicked.connect(self.handle_add)
        top_layout.addWidget(add_btn)
        
        layout.addWidget(top_section)
        
        # Create search section
        search_section = QFrame()
        search_section.setObjectName("search-section")
        search_layout = QHBoxLayout(search_section)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search cases...")
        self.search_input.setObjectName("search-input")
        self.search_input.textChanged.connect(self.handle_search)
        search_layout.addWidget(self.search_input)
        
        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.setObjectName("filter-combo")
        self.filter_combo.addItems(["All", "Open", "Closed", "Under Investigation", "Cold Case"])
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
        self.table.setObjectName("cases-table")
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Case Number", "Title", "Status", "Date Reported", "Closed Date"
        ])
        
        # Set table properties
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.doubleClicked.connect(lambda index: self.handle_edit(self.get_case_data(index.row())))
        
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
        self.refresh()
        
    def refresh(self):
        """Refresh the table data"""
        try:
            cases = self.case_model.get_all_cases()
            self.update_table(cases)
        except Exception as e:
            print(f"Error refreshing cases: {str(e)}")
            
    def update_table(self, cases):
        """Update table with filtered data"""
        self.table.setRowCount(len(cases))
        
        for row, case in enumerate(cases):
            self.table.setItem(row, 0, QTableWidgetItem(str(case['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(case['case_number']))
            self.table.setItem(row, 2, QTableWidgetItem(case['title']))
            self.table.setItem(row, 3, QTableWidgetItem(case['status']))
            self.table.setItem(row, 4, QTableWidgetItem(case['date_reported']))
            self.table.setItem(row, 5, QTableWidgetItem(case.get('closed_date', 'None')))
            
            # Set item properties
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    # Handle date formatting
                    if col in [4, 5]:  # date_reported and closed_date columns
                        date_str = item.text()
                        if date_str and date_str.strip():
                            try:
                                date = datetime.strptime(date_str, '%Y-%m-%d')
                                item.setText(date.strftime('%Y-%m-%d'))
                            except ValueError:
                                item.setText('')
                        else:
                            item.setText('')
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
    def get_case_data(self, row):
        """Get case data from table row"""
        case_id = int(self.table.item(row, 0).text())
        # Get complete case details including description and criminals
        return self.case_model.get_case_with_details(case_id)
        
    def handle_search(self, text):
        """Handle search input changes"""
        try:
            text = text.lower().strip()
            if text:
                cases = []
                all_cases = self.case_model.get_all_cases()
                for case in all_cases:
                    # Search in multiple fields
                    if (text in str(case['id']).lower() or
                        text in case['case_number'].lower() or
                        text in case['title'].lower() or
                        text in case['status'].lower() or
                        text in case['date_reported'].lower() or
                        text in str(case.get('closed_date', '')).lower()):
                        cases.append(case)
            else:
                cases = self.case_model.get_all_cases()
                
            self.update_table(cases)
            
        except Exception as e:
            print(f"Error searching cases: {str(e)}")
            
    def handle_filter(self, status):
        """Handle filter changes"""
        try:
            if status == "All":
                cases = self.case_model.get_all_cases()
            else:
                cases = self.case_model.get_cases_by_status(status)
                
            self.update_table(cases)
            
        except Exception as e:
            print(f"Error filtering cases: {str(e)}")
        
    def handle_add(self):
        """Handle add button click"""
        dialog = CaseDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.case_model.create_case(
                    dialog.submitted_data,
                    dialog.submitted_criminal_ids
                )
                self.refresh()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to create case record: {str(e)}",
                    QMessageBox.Ok
                )
                
    def handle_edit(self, case_data):
        """Handle row double click"""
        dialog = CaseDialog(self, case_data)
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.case_model.update_case(
                    case_data['id'],
                    dialog.submitted_data,
                    dialog.submitted_criminal_ids
                )
                self.refresh()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to update case record: {str(e)}",
                    QMessageBox.Ok
                ) 