from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QComboBox, QDateEdit,
                             QPushButton, QFileDialog, QFrame, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from typing import Dict, Any, Optional, List
from datetime import datetime

class FormWidget(QWidget):
    # Signals
    form_submitted = pyqtSignal(dict)  # Emitted when form is submitted
    form_cancelled = pyqtSignal()  # Emitted when form is cancelled
    
    def __init__(self, fields: List[Dict[str, Any]], parent=None):
        """
        Initialize FormWidget
        fields: List of dictionaries with field configurations
        Each field should have:
        - name: Field name
        - type: Field type (text, textarea, number, date, select, file)
        - label: Field label
        - required: Whether field is required
        - options: List of options for select fields
        """
        super().__init__(parent)
        self.fields = fields
        self.form_data = {}
        self.field_widgets = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Create form fields
        for field in self.fields:
            field_frame = QFrame()
            field_frame.setProperty('class', 'form-field')
            field_layout = QVBoxLayout(field_frame)
            field_layout.setSpacing(5)
            
            # Create label
            label = QLabel(field['label'])
            if field.get('required', False):
                label.setText(f"{field['label']} *")
            field_layout.addWidget(label)
            
            # Create field widget based on type
            widget = self.create_field_widget(field)
            self.field_widgets[field['name']] = widget
            field_layout.addWidget(widget)
            
            layout.addWidget(field_frame)
        
        layout.addStretch()
        
    def create_field_widget(self, field: Dict[str, Any]) -> QWidget:
        """Create appropriate widget based on field type"""
        field_type = field.get('type', 'text')
        
        if field_type == 'text':
            widget = QLineEdit()
            if 'placeholder' in field:
                widget.setPlaceholderText(field['placeholder'])
                
        elif field_type == 'textarea':
            widget = QTextEdit()
            if 'placeholder' in field:
                widget.setPlaceholderText(field['placeholder'])
                
        elif field_type == 'number':
            widget = QSpinBox()
            if 'min' in field:
                widget.setMinimum(field['min'])
            if 'max' in field:
                widget.setMaximum(field['max'])
                
        elif field_type == 'date':
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            widget.setDate(datetime.now().date())
            
        elif field_type == 'select':
            widget = QComboBox()
            if 'options' in field:
                for option in field['options']:
                    if isinstance(option, dict):
                        widget.addItem(option['label'], option['value'])
                    else:
                        widget.addItem(str(option))
                        
        elif field_type == 'file':
            widget = self.create_file_input(field)
            
        else:
            widget = QLineEdit()  # Default to text input
            
        return widget
        
    def create_file_input(self, field: Dict[str, Any]) -> QWidget:
        """Create a custom file input widget"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create hidden line edit to store file path
        file_path = QLineEdit()
        file_path.setReadOnly(True)
        if 'placeholder' in field:
            file_path.setPlaceholderText(field['placeholder'])
            
        # Create browse button
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(lambda: self.handle_file_browse(field, file_path))
        
        layout.addWidget(file_path)
        layout.addWidget(browse_btn)
        
        # Store line edit reference
        container.file_path = file_path
        
        return container
        
    def handle_file_browse(self, field: Dict[str, Any], file_path_widget: QLineEdit):
        """Handle file browse button click"""
        file_types = field.get('file_types', 'All Files (*.*)')
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            file_types
        )
        
        if file_path:
            file_path_widget.setText(file_path)
            
    def set_data(self, data: Dict[str, Any]):
        """Set form data"""
        self.form_data = data
        
        for field_name, widget in self.field_widgets.items():
            value = data.get(field_name)
            if value is not None:
                if isinstance(widget, QLineEdit):
                    widget.setText(str(value))
                elif isinstance(widget, QTextEdit):
                    widget.setText(str(value))
                elif isinstance(widget, QSpinBox):
                    widget.setValue(int(value))
                elif isinstance(widget, QDateEdit):
                    if isinstance(value, str):
                        widget.setDate(datetime.strptime(value, '%Y-%m-%d').date())
                    else:
                        widget.setDate(value)
                elif isinstance(widget, QComboBox):
                    index = widget.findData(value)
                    if index >= 0:
                        widget.setCurrentIndex(index)
                    else:
                        widget.setCurrentText(str(value))
                elif hasattr(widget, 'file_path'):
                    widget.file_path.setText(str(value))
                    
    def get_data(self) -> Dict[str, Any]:
        """Get form data"""
        data = {}
        
        for field in self.fields:
            widget = self.field_widgets[field['name']]
            
            if isinstance(widget, QLineEdit):
                value = widget.text()
            elif isinstance(widget, QTextEdit):
                value = widget.toPlainText()
            elif isinstance(widget, QSpinBox):
                value = widget.value()
            elif isinstance(widget, QDateEdit):
                value = widget.date().toPyDate()
            elif isinstance(widget, QComboBox):
                value = widget.currentData()
                if value is None:
                    value = widget.currentText()
            elif hasattr(widget, 'file_path'):
                value = widget.file_path.text()
            else:
                value = None
                
            data[field['name']] = value
            
        return data
        
    def validate(self) -> bool:
        """Validate form data"""
        for field in self.fields:
            if field.get('required', False):
                widget = self.field_widgets[field['name']]
                
                if isinstance(widget, QLineEdit):
                    if not widget.text().strip():
                        return False
                elif isinstance(widget, QTextEdit):
                    if not widget.toPlainText().strip():
                        return False
                elif hasattr(widget, 'file_path'):
                    if not widget.file_path.text().strip():
                        return False
                        
        return True
        
    def handle_submit(self):
        """Handle form submission"""
        if self.validate():
            self.form_submitted.emit(self.get_data())
        
    def handle_cancel(self):
        """Handle form cancellation"""
        self.form_cancelled.emit()
        
    def clear(self):
        """Clear form fields"""
        for widget in self.field_widgets.values():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QTextEdit):
                widget.clear()
            elif isinstance(widget, QSpinBox):
                widget.setValue(widget.minimum())
            elif isinstance(widget, QDateEdit):
                widget.setDate(datetime.now().date())
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif hasattr(widget, 'file_path'):
                widget.file_path.clear() 