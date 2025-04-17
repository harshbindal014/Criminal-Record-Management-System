import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from database.init_db import DatabaseInitializer
from ui.login_window import LoginWindow
from utils.log_config import setup_logging

# Setup root logger
logger = setup_logging('app')

def initialize_database():
    """Initialize the database"""
    try:
        db_init = DatabaseInitializer()
        db_init.init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        sys.exit(1)

def main():
    """Main application entry point"""
    # Initialize database
    initialize_database()
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Load and set stylesheet
    style_path = os.path.join('ui', 'styles', 'dark_theme.qss')
    if os.path.exists(style_path):
        with open(style_path, 'r') as f:
            app.setStyleSheet(f.read())
    
    # Create and show login window
    login = LoginWindow()
    login.show()
    
    # Start application event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 