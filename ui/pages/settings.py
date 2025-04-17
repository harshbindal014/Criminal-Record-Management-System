from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFrame, QMessageBox, QGroupBox, QLabel,
                             QSpinBox, QCheckBox, QComboBox, QLineEdit)
from PyQt5.QtCore import Qt
from models.user import UserModel
import json
import os

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_model = UserModel()
        self.settings_file = "settings.json"
        self.main_window = parent
        self.load_settings()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # User Settings
        user_group = QGroupBox("User Settings")
        user_layout = QVBoxLayout(user_group)
        
        # Change Password
        password_layout = QHBoxLayout()
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("Enter new password")
        
        change_password_btn = QPushButton("Change Password")
        change_password_btn.clicked.connect(self.change_password)
        
        password_layout.addWidget(self.new_password)
        password_layout.addWidget(change_password_btn)
        
        user_layout.addLayout(password_layout)
        
        layout.addWidget(user_group)
        
        # Display Settings
        display_group = QGroupBox("Display Settings")
        display_layout = QVBoxLayout(display_group)
        
        # Theme Selection
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Dark', 'Light'])
        self.theme_combo.setCurrentText(self.settings.get('theme', 'Dark'))
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        display_layout.addLayout(theme_layout)
        
        # Font Size
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font Size:"))
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(self.settings.get('font_size', 12))
        self.font_size.valueChanged.connect(self.apply_font_size)
        font_layout.addWidget(self.font_size)
        font_layout.addStretch()
        
        display_layout.addLayout(font_layout)
        
        layout.addWidget(display_group)
        
        # Data Settings
        data_group = QGroupBox("Data Settings")
        data_layout = QVBoxLayout(data_group)
        
        # Auto Refresh
        self.auto_refresh = QCheckBox("Enable Auto Refresh")
        self.auto_refresh.setChecked(self.settings.get('auto_refresh', True))
        self.auto_refresh.stateChanged.connect(self.save_settings)
        data_layout.addWidget(self.auto_refresh)
        
        # Refresh Interval
        refresh_layout = QHBoxLayout()
        refresh_layout.addWidget(QLabel("Refresh Interval (seconds):"))
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(5, 300)
        self.refresh_interval.setValue(self.settings.get('refresh_interval', 30))
        self.refresh_interval.valueChanged.connect(self.save_settings)
        refresh_layout.addWidget(self.refresh_interval)
        refresh_layout.addStretch()
        
        data_layout.addLayout(refresh_layout)
        
        layout.addWidget(data_group)
        
        # Export Settings
        export_group = QGroupBox("Export Settings")
        export_layout = QVBoxLayout(export_group)
        
        # Default Export Format
        export_format_layout = QHBoxLayout()
        export_format_layout.addWidget(QLabel("Default Export Format:"))
        self.export_format = QComboBox()
        self.export_format.addItems(['Excel', 'PDF'])
        self.export_format.setCurrentText(self.settings.get('default_export_format', 'Excel'))
        self.export_format.currentTextChanged.connect(self.save_settings)
        export_format_layout.addWidget(self.export_format)
        export_format_layout.addStretch()
        
        export_layout.addLayout(export_format_layout)
        
        layout.addWidget(export_group)
        
        # Save Button
        save_btn = QPushButton("Save All Settings")
        save_btn.setProperty('class', 'primary-button')
        save_btn.clicked.connect(self.save_all)
        
        layout.addWidget(save_btn)
        layout.addStretch()
        
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {
                    'theme': 'Dark',
                    'font_size': 12,
                    'auto_refresh': True,
                    'refresh_interval': 30,
                    'default_export_format': 'Excel'
                }
        except Exception:
            self.settings = {
                'theme': 'Dark',
                'font_size': 12,
                'auto_refresh': True,
                'refresh_interval': 30,
                'default_export_format': 'Excel'
            }
    
    def save_settings(self):
        """Save settings to file"""
        try:
            settings = {
                'theme': self.theme_combo.currentText(),
                'font_size': self.font_size.value(),
                'auto_refresh': self.auto_refresh.isChecked(),
                'refresh_interval': self.refresh_interval.value(),
                'default_export_format': self.export_format.currentText()
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
                
            self.settings = settings
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save settings: {str(e)}",
                QMessageBox.Ok
            )
    
    def save_all(self):
        """Save all settings and show confirmation"""
        self.save_settings()
        QMessageBox.information(
            self,
            "Success",
            "Settings saved successfully",
            QMessageBox.Ok
        )
    
    def change_password(self):
        """Change user password"""
        try:
            new_password = self.new_password.text()
            if new_password:
                self.user_model.change_password(new_password)
                self.new_password.clear()
                QMessageBox.information(
                    self,
                    "Success",
                    "Password changed successfully",
                    QMessageBox.Ok
                )
            else:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Please enter a new password",
                    QMessageBox.Ok
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to change password: {str(e)}",
                QMessageBox.Ok
            )
            
    def apply_theme(self, theme_name):
        """Apply the selected theme"""
        try:
            style_path = os.path.join("ui", "styles", f"{theme_name.lower()}_theme.qss")
            if os.path.exists(style_path):
                with open(style_path, "r") as f:
                    self.main_window.setStyleSheet(f.read())
                self.save_settings()
            else:
                QMessageBox.warning(
                    self,
                    "Warning",
                    f"Theme file not found: {style_path}",
                    QMessageBox.Ok
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to apply theme: {str(e)}",
                QMessageBox.Ok
            )
            
    def apply_font_size(self, size):
        """Apply the selected font size"""
        try:
            stylesheet = self.main_window.styleSheet()
            # Update the base font size in the stylesheet
            stylesheet = self.update_font_size_in_stylesheet(stylesheet, size)
            self.main_window.setStyleSheet(stylesheet)
            self.save_settings()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to apply font size: {str(e)}",
                QMessageBox.Ok
            )
            
    def update_font_size_in_stylesheet(self, stylesheet, size):
        """Update font size in the stylesheet"""
        import re
        # Update the base font size in QWidget
        stylesheet = re.sub(
            r'(QWidget\s*{[^}]*font-size:\s*)\d+px',
            rf'\g<1>{size}px',
            stylesheet
        )
        return stylesheet 