from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal

class BaseWidget(QWidget):
    """Base widget class with common functionality"""
    
    # Signals
    status_message = pyqtSignal(str, str)  # message, type (info, success, error, warning)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface - to be implemented by subclasses"""
        pass
    
    def show_error_message(self, title: str, message: str):
        """Show error message box"""
        QMessageBox.critical(self, title, message, QMessageBox.Ok)
    
    def show_warning_message(self, title: str, message: str):
        """Show warning message box"""
        QMessageBox.warning(self, title, message, QMessageBox.Ok)
    
    def show_info_message(self, title: str, message: str):
        """Show information message box"""
        QMessageBox.information(self, title, message, QMessageBox.Ok)
    
    def show_confirmation_dialog(self, title: str, message: str) -> bool:
        """Show confirmation dialog and return True if user clicks Yes"""
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def create_header(self, text: str) -> QLabel:
        """Create a header label with standard styling"""
        header = QLabel(text)
        header.setProperty('class', 'header-label')
        return header
    
    def create_sub_header(self, text: str) -> QLabel:
        """Create a sub-header label with standard styling"""
        sub_header = QLabel(text)
        sub_header.setProperty('class', 'sub-header-label')
        return sub_header
    
    def show_loading(self, message: str = "Loading..."):
        """Show loading state - to be implemented by subclasses"""
        pass
    
    def hide_loading(self):
        """Hide loading state - to be implemented by subclasses"""
        pass
    
    def clear_form(self):
        """Clear form fields - to be implemented by subclasses"""
        pass
    
    def validate_form(self) -> bool:
        """Validate form fields - to be implemented by subclasses"""
        return True
    
    def handle_error(self, error: Exception):
        """Handle errors in a consistent way"""
        error_message = str(error)
        self.status_message.emit(error_message, "error")
        self.show_error_message("Error", error_message)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable all form fields"""
        for widget in self.findChildren(QWidget):
            widget.setEnabled(enabled)
    
    def refresh(self):
        """Refresh widget data - to be implemented by subclasses"""
        pass 