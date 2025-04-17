from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
import bcrypt
import sqlite3
import logging
from utils.db_helper import DatabaseHelper
from models.user import UserModel
from ui.main_window import MainWindow

class LoginWindow(QMainWindow):
    login_successful = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.user_model = UserModel()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the login window UI"""
        self.setWindowTitle("Crime Record Management System - Login")
        self.setFixedSize(400, 500)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Add logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/images/logo.png")
        logo_label.setPixmap(logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        # Add system name
        system_name = QLabel("Crime Record Management System")
        system_name.setStyleSheet("font-size: 18px; font-weight: bold;")
        system_name.setAlignment(Qt.AlignCenter)
        layout.addWidget(system_name)
        
        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("padding: 8px;")
        layout.addWidget(self.username_input)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 8px;")
        layout.addWidget(self.password_input)
        
        # Login button
        login_button = QPushButton("Login")
        login_button.setStyleSheet("""
            QPushButton {
                padding: 8px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)
        
        # Set window icon
        self.setWindowIcon(QIcon("assets/images/icon.png"))
        
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return
            
        user = self.user_model.authenticate(username, password)
        
        if user:
            # Create and show main window
            from ui.main_window import MainWindow
            self.main_window = MainWindow(user)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
            self.password_input.clear()