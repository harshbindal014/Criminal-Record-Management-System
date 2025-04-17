from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor

class StatCard(QFrame):
    def __init__(self, title, value, icon_path, color, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.color = color
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Left section with icon
        icon_container = QFrame()
        icon_container.setObjectName("iconContainer")
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet(f"""
            #iconContainer {{
                background: {color};
                border-radius: 8px;
            }}
        """)
        
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(8, 8, 8, 8)
        
        # Load and set icon
        self.icon_label = QLabel()
        icon_pixmap = QPixmap(icon_path)
        if not icon_pixmap.isNull():
            icon_pixmap = icon_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(icon_pixmap)
        icon_layout.addWidget(self.icon_label, 0, Qt.AlignCenter)
        
        layout.addWidget(icon_container)
        
        # Right section with text
        text_container = QFrame()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)
        
        # Value
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("statValue")
        text_layout.addWidget(self.value_label)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("statTitle")
        text_layout.addWidget(self.title_label)
        
        layout.addWidget(text_container, 1)
        
        # Set styling
        self.setStyleSheet(f"""
            #statCard {{
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
            }}
            #statValue {{
                font-size: 24px;
                font-weight: bold;
                color: #202124;
            }}
            #statTitle {{
                font-size: 14px;
                color: #5f6368;
            }}
        """)
        
        # Set fixed size
        self.setFixedHeight(100)
        self.setFixedWidth(280)

    def update_value(self, value):
        """Update the card's value"""
        self.value_label.setText(str(value)) 