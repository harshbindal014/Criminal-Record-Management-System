from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLineEdit, QComboBox,
                             QPushButton, QLabel, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Dict, Any, Optional
import math

class DataTable(QWidget):
    # Signals
    row_selected = pyqtSignal(dict)  # Emitted when a row is selected
    row_double_clicked = pyqtSignal(dict)  # Emitted when a row is double-clicked
    
    def __init__(self, columns: List[Dict[str, str]], page_size: int = 10,
                 searchable: bool = True, parent=None):
        """
        Initialize DataTable
        columns: List of dictionaries with 'key' and 'title' for each column
        page_size: Number of rows per page
        searchable: Whether to show search functionality
        """
        super().__init__(parent)
        self.columns = columns
        self.page_size = page_size
        self.searchable = searchable
        self.current_page = 1
        self.total_pages = 1
        self.filtered_data = []
        self.all_data = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create search bar if searchable
        if self.searchable:
            search_frame = QFrame()
            search_frame.setObjectName("search-frame")
            search_layout = QHBoxLayout(search_frame)
            search_layout.setContentsMargins(0, 0, 0, 10)
            
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Search...")
            self.search_input.setObjectName("search-input")
            self.search_input.textChanged.connect(self.handle_search)
            
            self.filter_combo = QComboBox()
            self.filter_combo.setObjectName("filter-combo")
            self.filter_combo.addItem("All Columns")
            for col in self.columns:
                self.filter_combo.addItem(col['title'])
            
            search_layout.addWidget(self.search_input)
            search_layout.addWidget(self.filter_combo)
            layout.addWidget(search_frame)
        
        # Create table container
        table_container = QFrame()
        table_container.setObjectName("table-container")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(1, 1, 1, 1)
        table_layout.setSpacing(0)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels([col['title'] for col in self.columns])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setShowGrid(False)
        
        # Connect signals
        self.table.itemSelectionChanged.connect(self.handle_selection)
        self.table.itemDoubleClicked.connect(self.handle_double_click)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_container)
        
        # Create pagination controls
        pagination_frame = QFrame()
        pagination_frame.setObjectName("pagination-frame")
        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(0, 10, 0, 0)
        
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.setObjectName("pagination-button")
        
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setObjectName("page-label")
        
        self.next_btn = QPushButton("Next")
        self.next_btn.setObjectName("pagination-button")
        
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addStretch()
        
        self.prev_btn.clicked.connect(self.previous_page)
        self.next_btn.clicked.connect(self.next_page)
        
        layout.addWidget(pagination_frame)
        
        self.setStyleSheet("""
            QWidget {
                background: white;
                color: #202124;
            }
            #search-frame {
                background: transparent;
            }
            #search-input {
                border: 1px solid #dadce0;
                border-radius: 4px;
                padding: 8px 12px;
                min-height: 36px;
                color: #202124;
                background: white;
            }
            #search-input:focus {
                border: 2px solid #1a73e8;
                outline: none;
            }
            #filter-combo {
                border: 1px solid #dadce0;
                border-radius: 4px;
                padding: 8px 12px;
                min-width: 150px;
                margin-left: 10px;
                color: #202124;
                background: white;
            }
            #filter-combo:focus {
                border: 2px solid #1a73e8;
                outline: none;
            }
            #table-container {
                border: 1px solid #dadce0;
                border-radius: 8px;
                background: white;
            }
            QTableWidget {
                border: none;
                background: white;
                gridline-color: #f1f3f4;
                color: #202124;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f1f3f4;
                color: #202124;
                background: white;
            }
            QTableWidget::item:selected {
                background: #e8f0fe;
                color: #202124;
            }
            QTableWidget::item:alternate {
                background: #f8f9fa;
                color: #202124;
            }
            QHeaderView::section {
                background: #f8f9fa;
                color: #5f6368;
                font-weight: 500;
                padding: 12px;
                border: none;
                border-bottom: 1px solid #dadce0;
            }
            QHeaderView {
                background: white;
            }
            #pagination-frame {
                background: transparent;
            }
            #pagination-button {
                background: white;
                border: 1px solid #dadce0;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 100px;
                color: #202124;
            }
            #pagination-button:hover {
                background: #f8f9fa;
            }
            #pagination-button:disabled {
                color: #5f6368;
                background: #f8f9fa;
            }
            #page-label {
                color: #5f6368;
                margin: 0 16px;
                min-width: 100px;
            }
        """)
        
    def set_data(self, data: List[Dict[str, Any]]):
        """Set table data and refresh display"""
        self.all_data = data
        self.filtered_data = data.copy()
        self.current_page = 1
        self.refresh_table()
        
    def refresh_table(self):
        """Refresh table display"""
        # Calculate pagination
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_data = self.filtered_data[start_idx:end_idx]
        
        # Update table
        self.table.setRowCount(len(page_data))
        
        for row_idx, row_data in enumerate(page_data):
            for col_idx, col_info in enumerate(self.columns):
                value = str(row_data.get(col_info['key'], ''))
                item = QTableWidgetItem(value)
                item.setData(Qt.UserRole, row_data)  # Store full row data
                self.table.setItem(row_idx, col_idx, item)
        
        # Update pagination controls
        self.total_pages = math.ceil(len(self.filtered_data) / self.page_size)
        self.page_label.setText(f"Page {self.current_page} of {self.total_pages}")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)
        
    def handle_search(self, search_text: str):
        """Handle search input changes"""
        if not search_text:
            self.filtered_data = self.all_data.copy()
        else:
            search_text = search_text.lower()
            selected_column = self.filter_combo.currentText()
            
            if selected_column == "All Columns":
                # Search in all columns
                self.filtered_data = [
                    row for row in self.all_data
                    if any(
                        search_text in str(row.get(col['key'], '')).lower()
                        for col in self.columns
                    )
                ]
            else:
                # Search in selected column
                search_key = next(
                    col['key'] for col in self.columns
                    if col['title'] == selected_column
                )
                self.filtered_data = [
                    row for row in self.all_data
                    if search_text in str(row.get(search_key, '')).lower()
                ]
        
        self.current_page = 1
        self.refresh_table()
        
    def handle_selection(self):
        """Handle row selection"""
        selected_items = self.table.selectedItems()
        if selected_items:
            row_data = selected_items[0].data(Qt.UserRole)
            self.row_selected.emit(row_data)
            
    def handle_double_click(self, item):
        """Handle row double click"""
        row_data = item.data(Qt.UserRole)
        self.row_double_clicked.emit(row_data)
        
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.refresh_table()
            
    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_table()
            
    def clear_selection(self):
        """Clear table selection"""
        self.table.clearSelection()
        
    def get_selected_data(self) -> Optional[Dict[str, Any]]:
        """Get data from selected row"""
        selected_items = self.table.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.UserRole)
        return None 