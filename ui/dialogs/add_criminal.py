from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QPushButton, QFrame,
                             QFileDialog, QMessageBox, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from models.criminal import CriminalModel
from datetime import datetime

class AddCriminalDialog(QDialog):
    criminal_added = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.criminal_model = CriminalModel()
        self.selected_image_path = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Add New Criminal")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter criminal's name")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Age input
        age_layout = QHBoxLayout()
        age_label = QLabel("Age:")
        self.age_input = QSpinBox()
        self.age_input.setRange(18, 100)
        self.age_input.setValue(25)
        age_layout.addWidget(age_label)
        age_layout.addWidget(self.age_input)
        layout.addLayout(age_layout)
        
        # Gender input
        gender_layout = QHBoxLayout()
        gender_label = QLabel("Gender:")
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female", "Other"])
        gender_layout.addWidget(gender_label)
        gender_layout.addWidget(self.gender_input)
        layout.addLayout(gender_layout)
        
        # Crime Type input
        crime_layout = QHBoxLayout()
        crime_label = QLabel("Crime Type:")
        self.crime_input = QComboBox()
        self.crime_input.addItems(["Theft", "Assault", "Fraud", "Drug Possession", "Other"])
        crime_layout.addWidget(crime_label)
        crime_layout.addWidget(self.crime_input)
        layout.addLayout(crime_layout)
        
        # Status input
        status_layout = QHBoxLayout()
        status_label = QLabel("Status:")
        self.status_input = QComboBox()
        self.status_input.addItems(["Wanted", "Arrested", "Released"])
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_input)
        layout.addLayout(status_layout)
        
        # Image upload
        image_layout = QHBoxLayout()
        self.image_label = QLabel("No image selected")
        choose_image_btn = QPushButton("Choose Image")
        choose_image_btn.clicked.connect(self.choose_image)
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(choose_image_btn)
        layout.addLayout(image_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_criminal)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Apply styles
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
                min-width: 200px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
                background-color: #2196F3;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton[text="Cancel"] {
                background-color: #f44336;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #d32f2f;
            }
        """)
        
    def choose_image(self):
        """Open file dialog to choose image"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Criminal Image",
            "",
            "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_name:
            self.selected_image_path = file_name
            self.image_label.setText(file_name.split('/')[-1])
            
    def save_criminal(self):
        """Save criminal record"""
        try:
            # Validate inputs
            name = self.name_input.text().strip()
            if not name:
                raise ValueError("Name is required")
                
            age = self.age_input.text().strip()
            if not age.isdigit():
                raise ValueError("Age must be a number")
                
            # Create data dictionary
            data = {
                'name': name,
                'age': int(age),
                'gender': self.gender_input.currentText(),
                'crime_type': self.crime_input.currentText(),
                'status': self.status_input.currentText(),
                'arrest_date': None if self.status_input.currentText() == 'Wanted' else datetime.now().strftime('%Y-%m-%d')
            }
            
            # Add image if selected
            if hasattr(self, 'selected_image_path'):
                data['image_path'] = self.selected_image_path
            
            # Create record
            self.criminal_model.create_with_image(data)
            self.criminal_added.emit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                str(e),
                QMessageBox.Ok
            ) 