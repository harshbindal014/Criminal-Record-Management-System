from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class ActivityItem(QWidget):
    def __init__(self, activity_data):
        super().__init__()
        self.setup_ui(activity_data)
        
    def setup_ui(self, activity_data):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Title
        title = QLabel(activity_data.get('title', ''))
        title.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #202124;
                font-size: 14px;
            }
        """)
        layout.addWidget(title)
        
        # Description
        description = QLabel(activity_data.get('description', ''))
        description.setStyleSheet("""
            QLabel {
                color: #5f6368;
                font-size: 13px;
            }
        """)
        layout.addWidget(description)
        
        # Time
        time = QLabel(activity_data.get('time', ''))
        time.setStyleSheet("""
            QLabel {
                color: #5f6368;
                font-size: 12px;
            }
        """)
        layout.addWidget(time)
        
        self.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 4px;
            }
            QWidget:hover {
                background: #f8f9fa;
            }
        """) 