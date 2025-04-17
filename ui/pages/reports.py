from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFrame, QMessageBox, QFileDialog, QLabel,
                             QComboBox, QDateEdit, QGroupBox, QSizePolicy,
                             QScrollArea)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QPainter, QFont
from models.case import CaseModel
from models.criminal import CriminalModel
from models.evidence import EvidenceModel
from utils.export_helper import export_to_excel, export_to_pdf
from datetime import datetime, timedelta
import os
import csv

class ReportButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumWidth(300)  # Reduced for horizontal layout
        self.setMinimumHeight(48)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.setText(text)
        
        self.setStyleSheet("""
            ReportButton {
                background: white;
                color: #0066ff;
                border: 1px solid #0066ff;
                padding: 12px 20px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 14px;
                text-align: center;
            }
            ReportButton:hover {
                background: #f0f7ff;
            }
            ReportButton:pressed {
                background: #e6f0ff;
            }
        """)

    def sizeHint(self):
        return QSize(300, 48)  # Fixed size for consistent layout

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect().adjusted(16, 8, -16, -8)  # Add padding
        
        # Draw text with word wrap
        painter.setPen(self.palette().color(self.foregroundRole()))
        painter.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter | Qt.TextWordWrap, self.text())

class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.case_model = CaseModel()
        self.criminal_model = CriminalModel()
        self.evidence_model = EvidenceModel()
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setStyleSheet("background-color: #ffffff;")

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)  # Remove frame
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 12px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
                border: none;
                background: none;
            }
        """)

        # Container Widget
        container = QWidget()
        container.setStyleSheet("background-color: #ffffff;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(24, 24, 24, 24)
        container_layout.setSpacing(20)

        # Reports Section
        reports_group = QGroupBox("Generate Reports")
        reports_group.setStyleSheet("""
            QGroupBox {
                background-color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                padding-top: 32px;
                border: none;
                margin-top: 16px;
            }
            QGroupBox::title {
                color: #0f172a;
                padding: 0 12px;
                background-color: #ffffff;
            }
        """)
        reports_layout = QVBoxLayout(reports_group)
        reports_layout.setContentsMargins(24, 40, 24, 24)
        reports_layout.setSpacing(24)

        # Date Range Section
        date_section = QFrame()
        date_section.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        date_layout = QVBoxLayout(date_section)
        date_layout.setSpacing(16)

        date_label = QLabel("Select Date Range")
        date_label.setStyleSheet("color: #475569; font-size: 16px; font-weight: 600;")
        date_layout.addWidget(date_label)

        date_inputs = QHBoxLayout()
        date_inputs.setSpacing(24)

        # Start Date
        start_date_container = QVBoxLayout()
        start_date_label = QLabel("Start Date")
        start_date_label.setStyleSheet("color: #64748b; font-size: 14px;")
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.style_date_input(self.start_date)
        start_date_container.addWidget(start_date_label)
        start_date_container.addWidget(self.start_date)
        date_inputs.addLayout(start_date_container)

        # End Date
        end_date_container = QVBoxLayout()
        end_date_label = QLabel("End Date")
        end_date_label.setStyleSheet("color: #64748b; font-size: 14px;")
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.style_date_input(self.end_date)
        end_date_container.addWidget(end_date_label)
        end_date_container.addWidget(self.end_date)
        date_inputs.addLayout(end_date_container)

        date_inputs.addStretch()
        date_layout.addLayout(date_inputs)
        reports_layout.addWidget(date_section)

        # Export Format Section
        format_section = QFrame()
        format_section.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        format_layout = QVBoxLayout(format_section)
        format_layout.setSpacing(16)

        format_label = QLabel("Export Format")
        format_label.setStyleSheet("color: #475569; font-size: 16px; font-weight: 600;")
        format_layout.addWidget(format_label)

        format_container = QHBoxLayout()
        format_select_label = QLabel("Select Format")
        format_select_label.setStyleSheet("color: #64748b; font-size: 14px;")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Excel", "PDF", "CSV"])
        self.style_combo_input(self.format_combo)
        format_container.addWidget(format_select_label)
        format_container.addWidget(self.format_combo)
        format_container.addStretch()
        format_layout.addLayout(format_container)
        reports_layout.addWidget(format_section)

        # Available Reports Section
        available_reports_section = QFrame()
        available_reports_section.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        available_reports_layout = QVBoxLayout(available_reports_section)
        available_reports_layout.setSpacing(24)

        reports_label = QLabel("Available Reports")
        reports_label.setStyleSheet("color: #475569; font-size: 16px; font-weight: 600;")
        available_reports_layout.addWidget(reports_label)

        # Case Reports
        case_reports = QVBoxLayout()
        case_reports_label = QLabel("Case Reports")
        case_reports_label.setStyleSheet("color: #64748b; font-size: 14px; font-weight: 600;")
        case_reports.addWidget(case_reports_label)

        case_buttons = QHBoxLayout()
        case_buttons.setSpacing(16)
        case_buttons.addWidget(self.create_report_button("Generate Case Status Report", lambda: self.generate_case_report('status')))
        case_buttons.addWidget(self.create_report_button("Generate Case Timeline Report", lambda: self.generate_case_report('timeline')))
        case_buttons.addStretch()
        case_reports.addLayout(case_buttons)
        available_reports_layout.addLayout(case_reports)

        # Criminal Reports
        criminal_reports = QVBoxLayout()
        criminal_reports_label = QLabel("Criminal Reports")
        criminal_reports_label.setStyleSheet("color: #64748b; font-size: 14px; font-weight: 600;")
        criminal_reports.addWidget(criminal_reports_label)

        criminal_buttons = QHBoxLayout()
        criminal_buttons.setSpacing(16)
        criminal_buttons.addWidget(self.create_report_button("Generate Criminal Status Report", lambda: self.generate_criminal_report('stats')))
        criminal_buttons.addWidget(self.create_report_button("Generate Criminal History Report", lambda: self.generate_criminal_report('history')))
        criminal_buttons.addStretch()
        criminal_reports.addLayout(criminal_buttons)
        available_reports_layout.addLayout(criminal_reports)

        # Evidence Reports
        evidence_reports = QVBoxLayout()
        evidence_reports_label = QLabel("Evidence Reports")
        evidence_reports_label.setStyleSheet("color: #64748b; font-size: 14px; font-weight: 600;")
        evidence_reports.addWidget(evidence_reports_label)

        evidence_buttons = QHBoxLayout()
        evidence_buttons.setSpacing(16)
        evidence_buttons.addWidget(self.create_report_button("Generate Evidence Inventory Report", lambda: self.generate_evidence_report('inventory')))
        evidence_buttons.addWidget(self.create_report_button("Generate Chain of Custody Report", lambda: self.generate_evidence_report('custody')))
        evidence_buttons.addStretch()
        evidence_reports.addLayout(evidence_buttons)
        available_reports_layout.addLayout(evidence_reports)

        reports_layout.addWidget(available_reports_section)
        container_layout.addWidget(reports_group)

        # Set the container as the scroll area widget
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def create_report_button(self, text, callback):
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc;
                color: #0f172a;
                border: 2px solid #e2e8f0;
                padding: 16px 32px;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                min-width: 300px;
                min-height: 60px;
            }
            QPushButton:hover {
                background-color: #2563eb;
                border-color: #2563eb;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
                border-color: #1d4ed8;
                color: #ffffff;
            }
        """)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(callback)
        return button

    def style_date_input(self, widget):
        widget.setStyleSheet("""
            QDateEdit {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 220px;
                min-height: 40px;
                color: #0f172a;
                font-size: 14px;
            }
            QDateEdit:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
            QDateEdit:focus {
                border-color: #2563eb;
                background-color: #ffffff;
            }
            QDateEdit::drop-down {
                border: none;
                width: 20px;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #64748b;
                margin-right: 8px;
            }
            QCalendarWidget {
                background-color: #ffffff;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
            }
            QCalendarWidget QWidget {
                alternate-background-color: #ffffff;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #0f172a;
                background-color: #ffffff;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #94a3b8;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #ffffff;
                padding: 4px;
            }
            QCalendarWidget QToolButton {
                color: #0f172a;
                background-color: #ffffff;
                padding: 6px;
                border-radius: 4px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #f1f5f9;
            }
            QCalendarWidget QSpinBox {
                color: #0f172a;
                background-color: #ffffff;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
            }
        """)

    def style_combo_input(self, widget):
        widget.setStyleSheet("""
            QComboBox {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 220px;
                min-height: 40px;
                color: #0f172a;
                font-size: 14px;
            }
            QComboBox:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
            QComboBox:focus {
                border-color: #2563eb;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #64748b;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 4px;
                color: #0f172a;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
            }
            QComboBox QAbstractItemView::item {
                min-height: 28px;
                padding: 8px 16px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #f1f5f9;
            }
        """)

    def generate_case_report(self, report_type):
        """Generate case-related reports"""
        try:
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            
            if report_type == 'status':
                data = self.case_model.get_status_report(start_date, end_date)
                title = "Case Status Report"
            else:  # timeline
                data = self.case_model.get_timeline_report(start_date, end_date)
                title = "Case Timeline Report"
            
            self.export_report(data, title)
            
        except Exception as e:
            self.show_error("Failed to generate case report", str(e))
    
    def generate_criminal_report(self, report_type):
        """Generate criminal-related reports"""
        try:
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            
            if report_type == 'stats':
                data = self.criminal_model.get_statistics_report(start_date, end_date)
                title = "Criminal Statistics Report"
            else:  # history
                data = self.criminal_model.get_history_report(start_date, end_date)
                title = "Criminal History Report"
            
            self.export_report(data, title)
            
        except Exception as e:
            self.show_error("Failed to generate criminal report", str(e))
    
    def generate_evidence_report(self, report_type):
        """Generate evidence-related reports"""
        try:
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            
            if report_type == 'inventory':
                data = self.evidence_model.get_inventory_report(start_date, end_date)
                title = "Evidence Inventory Report"
            else:  # custody
                data = self.evidence_model.get_custody_report(start_date, end_date)
                title = "Chain of Custody Report"
            
            self.export_report(data, title)
            
        except Exception as e:
            self.show_error("Failed to generate evidence report", str(e))
    
    def export_report(self, data, title):
        """Export report data to selected format"""
        try:
            # Get save file location
            file_format = self.format_combo.currentText()
            default_name = f"{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if file_format == 'Excel':
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Report",
                    default_name,
                    "Excel Files (*.xlsx)"
                )
                if file_path:
                    # Ensure the file has .xlsx extension
                    if not file_path.lower().endswith('.xlsx'):
                        file_path += '.xlsx'
                    export_to_excel(data, file_path)
            elif file_format == 'PDF':
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Report",
                    default_name,
                    "PDF Files (*.pdf)"
                )
                if file_path:
                    # Ensure the file has .pdf extension
                    if not file_path.lower().endswith('.pdf'):
                        file_path += '.pdf'
                    export_to_pdf(data, file_path, title)
            else:  # CSV
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Report",
                    default_name,
                    "CSV Files (*.csv)"
                )
                if file_path:
                    # Ensure the file has .csv extension
                    if not file_path.lower().endswith('.csv'):
                        file_path += '.csv'
                    with open(file_path, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerows(data)
            
            if file_path:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Report exported successfully to {file_path}",
                    QMessageBox.Ok
                )
                
        except Exception as e:
            self.show_error("Failed to export report", str(e))
    
    def show_error(self, title, message):
        """Show error message"""
        QMessageBox.critical(
            self,
            title,
            message,
            QMessageBox.Ok
        ) 