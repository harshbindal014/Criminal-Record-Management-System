import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QStackedWidget, QFrame, QSpacerItem,
                             QSizePolicy)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor
from ui.pages.dashboard import DashboardPage
from ui.pages.criminals import CriminalsPage
from ui.pages.cases import CasesPage
from ui.pages.evidence import EvidencePage
from ui.pages.reports import ReportsPage
from ui.pages.settings import SettingsPage
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("Crime Record Management System")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Add logo section
        logo_frame = QFrame()
        logo_frame.setObjectName("logoSection")
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(24, 24, 24, 24)
        
        system_name = QLabel("CRM System")
        system_name.setObjectName("systemName")
        logo_layout.addWidget(system_name)
        sidebar_layout.addWidget(logo_frame)
        
        # Navigation buttons
        nav_items = [
            ("Dashboard", "dashboard.svg", self.show_dashboard),
            ("Criminals", "criminal.svg", self.show_criminals),
            ("Cases", "case.svg", self.show_cases),
            ("Evidence", "evidence.svg", self.show_evidence),
            ("Reports", "report.svg", self.show_reports)
        ]
        
        # Add nav section
        nav_section = QFrame()
        nav_section.setObjectName("navSection")
        nav_layout = QVBoxLayout(nav_section)
        nav_layout.setContentsMargins(0, 12, 0, 12)
        nav_layout.setSpacing(4)
        
        self.nav_buttons = []
        for text, icon, handler in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("navButton")
            btn.setIcon(QIcon(f"assets/icons/{icon}"))
            btn.setIconSize(QSize(20, 20))
            btn.clicked.connect(handler)
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        sidebar_layout.addWidget(nav_section)
        
        # Add spacer
        sidebar_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Add logout section
        logout_section = QFrame()
        logout_section.setObjectName("logoutSection")
        logout_layout = QVBoxLayout(logout_section)
        logout_layout.setContentsMargins(0, 12, 0, 12)
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("logoutButton")
        logout_btn.setIcon(QIcon("assets/icons/logout.svg"))
        logout_btn.setIconSize(QSize(20, 20))
        logout_btn.clicked.connect(self.handle_logout)
        logout_layout.addWidget(logout_btn)
        
        sidebar_layout.addWidget(logout_section)
        
        main_layout.addWidget(self.sidebar)
        
        # Create main content area
        content_container = QFrame()
        content_container.setObjectName("contentContainer")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Add header bar
        header_bar = QFrame()
        header_bar.setObjectName("headerBar")
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(24, 0, 24, 0)
        header_layout.setSpacing(16)
        
        # Add system name to header
        header_title = QLabel("Crime Record Management System")
        header_title.setObjectName("headerTitle")
        header_layout.addWidget(header_title)
        
        # Add spacer to push admin info to right
        header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Add admin info
        admin_label = QLabel("Admin")
        admin_label.setObjectName("adminLabel")
        header_layout.addWidget(admin_label)
        
        # Add time
        self.time_label = QLabel()
        self.time_label.setObjectName("timeLabel")
        self.update_time()
        
        # Setup timer for clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        header_layout.addWidget(self.time_label)
        content_layout.addWidget(header_bar)
        
        # Add main content
        main_content = QFrame()
        main_content.setObjectName("mainContent")
        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.setContentsMargins(24, 24, 24, 24)
        main_content_layout.setSpacing(24)
        
        # Add stacked widget for pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stackedWidget")
        
        # Initialize pages
        self.dashboard_page = DashboardPage()
        self.criminals_page = CriminalsPage()
        self.cases_page = CasesPage()
        self.evidence_page = EvidencePage()
        self.reports_page = ReportsPage()
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.criminals_page)
        self.stacked_widget.addWidget(self.cases_page)
        self.stacked_widget.addWidget(self.evidence_page)
        self.stacked_widget.addWidget(self.reports_page)
        
        main_content_layout.addWidget(self.stacked_widget)
        content_layout.addWidget(main_content)
        main_layout.addWidget(content_container)
        
        # Set active nav button
        self.nav_buttons[0].setProperty("active", True)
        self.nav_buttons[0].style().unpolish(self.nav_buttons[0])
        self.nav_buttons[0].style().polish(self.nav_buttons[0])
        
        # Apply stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background: white;
            }
            #sidebar {
                background: #2563eb;
                min-width: 250px;
                max-width: 250px;
            }
            #logoSection {
                background: rgba(0, 0, 0, 0.1);
                min-height: 64px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            #systemName {
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI';
            }
            #navSection {
                background: transparent;
            }
            #navButton, #logoutButton {
                background: transparent;
                border: none;
                color: white;
                text-align: left;
                padding: 12px 24px;
                font-size: 14px;
                font-family: 'Segoe UI';
                border-radius: 4px;
                margin: 0 12px;
            }
            #navButton:hover, #logoutButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            #navButton[active="true"] {
                background: rgba(0, 0, 0, 0.2);
            }
            #logoutSection {
                background: transparent;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
            #contentContainer {
                background: white;
            }
            #headerBar {
                background: white;
                border-bottom: 1px solid #e5e7eb;
                min-height: 64px;
            }
            #headerTitle {
                color: #212529;
                font-size: 16px;
                font-weight: 500;
                font-family: 'Segoe UI';
            }
            #adminLabel, #timeLabel {
                color: #6c757d;
                font-size: 14px;
                font-family: 'Segoe UI';
            }
            #mainContent {
                background: white;
            }
            #welcomeContainer {
                background: transparent;
            }
            #welcomeTitle {
                color: #212529;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI';
            }
            #welcomeSubtitle {
                color: #6c757d;
                font-size: 14px;
                font-family: 'Segoe UI';
            }
            #stackedWidget {
                background: white;
            }
            QPushButton {
                text-align: left;
                padding-left: 12px;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
            QFrame {
                background: transparent;
            }
        """)

    def update_time(self):
        current_time = datetime.now().strftime("%I:%M %p")
        self.time_label.setText(current_time)
        
    def show_dashboard(self):
        self.stacked_widget.setCurrentIndex(0)
        self.update_active_nav_button(0)
        
    def show_criminals(self):
        self.stacked_widget.setCurrentIndex(1)
        self.update_active_nav_button(1)
        
    def show_cases(self):
        self.stacked_widget.setCurrentIndex(2)
        self.update_active_nav_button(2)
        
    def show_evidence(self):
        self.stacked_widget.setCurrentIndex(3)
        self.update_active_nav_button(3)
        
    def show_reports(self):
        self.stacked_widget.setCurrentIndex(4)
        self.update_active_nav_button(4)
        
    def update_active_nav_button(self, active_index):
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", i == active_index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            
    def handle_logout(self):
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close() 