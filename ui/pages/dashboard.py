from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
                           QSizePolicy, QPushButton, QDateEdit)
from PyQt5.QtChart import (QChart, QChartView, QPieSeries, QLineSeries,
                           QValueAxis, QDateTimeAxis, QSplineSeries, QLegend, QPieSlice)
from PyQt5.QtCore import Qt, QDateTime, QTimer, QMargins, QDate, QTime
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush
from ui.widgets.stat_card import StatCard
from models.criminal import CriminalModel
from models.case import CaseModel
from models.evidence import EvidenceModel

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.criminal_model = CriminalModel()
        self.case_model = CaseModel()
        self.evidence_model = EvidenceModel()
        self.setup_ui()
        
        # Setup refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
    def setup_ui(self):
        """Setup the user interface"""
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Welcome section
        welcome_section = QFrame()
        welcome_section.setObjectName("welcome-section")
        welcome_layout = QVBoxLayout(welcome_section)
        welcome_layout.setContentsMargins(0, 0, 0, 20)
        welcome_layout.setSpacing(5)
        
        welcome_title = QLabel("Welcome to Dashboard")
        welcome_title.setObjectName("welcomeTitle")
        welcome_layout.addWidget(welcome_title)
        
        welcome_subtitle = QLabel("Monitor and analyze your system's key metrics")
        welcome_subtitle.setObjectName("welcomeSubtitle")
        welcome_layout.addWidget(welcome_subtitle)
        
        layout.addWidget(welcome_section)

        # Stats section
        stats_section = QFrame()
        stats_section.setObjectName("stats-section")
        stats_layout = QHBoxLayout(stats_section)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(20)
        
        # Add stat cards
        self.create_stat_cards(stats_layout)
        layout.addWidget(stats_section)

        # Charts section
        charts_section = QFrame()
        charts_section.setObjectName("charts-section")
        charts_layout = QHBoxLayout(charts_section)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(20)
        
        # Add charts
        self.create_charts(charts_layout)
        layout.addWidget(charts_section)

        # Set styling
        self.setStyleSheet("""
            QWidget {
                background: white;
                color: #202124;
            }
            #welcomeTitle {
                font-size: 24px;
                font-weight: bold;
                color: #202124;
                font-family: 'Segoe UI';
            }
            #welcomeSubtitle {
                font-size: 14px;
                color: #5f6368;
                font-family: 'Segoe UI';
            }
            #chartContainer {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            #chartTitle {
                font-size: 16px;
                font-weight: bold;
                color: #202124;
                font-family: 'Segoe UI';
            }
        """)
        
        # Initial data load
        self.refresh()
        
    def create_pie_chart(self):
        """Create pie chart with real crime type distribution"""
        series = QPieSeries()
        series.setHoleSize(0.45)  # Increased hole size for better appearance
        
        try:
            # Get actual crime type distribution from database
            crime_stats = self.criminal_model.get_crime_type_stats()
            total_criminals = sum(int(stat['count']) for stat in crime_stats)
            
            # Completely distinct color palette with high contrast between adjacent colors
            color_map = {
                "Theft": "#2563eb",          # Royal Blue
                "Assault": "#dc2626",        # Red
                "Fraud": "#eab308",          # Golden Yellow
                "Drug Trafficking": "#059669", # Emerald Green
                "Homicide": "#7c3aed",       # Purple
                "Cybercrime": "#0ea5e9",     # Light Blue
                "Kidnapping": "#ec4899",     # Pink
                "Burglary": "#f97316",       # Orange
                "Embezzlement": "#14b8a6",   # Teal
                "Drug Possession": "#84cc16", # Lime
                "Vandalism": "#6366f1",      # Indigo
                "Identity Theft": "#06b6d4",  # Cyan
                "Arson": "#be123c",          # Ruby Red
                "Money Laundering": "#854d0e", # Dark Amber
                "Racketeering": "#7e22ce",   # Deep Purple
                "Prostitution": "#ca8a04",   # Dark Yellow
                "Terrorism": "#991b1b",      # Dark Red
                "Human Trafficking": "#0f766e", # Dark Teal
                "Other": "#64748b"           # Slate Gray
            }
            
            # Sort crime stats by count to ensure consistent color assignment
            crime_stats = sorted(crime_stats, key=lambda x: int(x['count']), reverse=True)
            
            # Add data points with exploded slices for emphasis
            for stat in crime_stats:
                crime_type = stat['crime_type']
                count = int(stat['count'])
                percentage = (count / total_criminals) * 100 if total_criminals > 0 else 0
                
                slice = series.append(crime_type, percentage)
                slice.setColor(QColor(color_map.get(crime_type, "#64748b")))
                slice.setLabelVisible(True)
                slice.setLabelPosition(QPieSlice.LabelOutside)  # Position labels outside
                
                # Format label with crime type and percentage
                slice.setLabel(f"{crime_type}\n{percentage:.1f}%")
                
                # Explode important slices
                if percentage > 15:  # Explode slices with more than 15%
                    slice.setExploded(True)
                    slice.setExplodeDistanceFactor(0.1)
        
        except Exception as e:
            print(f"Error creating pie chart: {str(e)}")
            # Add dummy data if there's an error
            series.append("No Data", 100)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setBackgroundVisible(False)
        chart.setAnimationOptions(QChart.SeriesAnimations)  # Add animations
        
        # Configure legend
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignRight)
        chart.legend().setFont(QFont("Segoe UI", 9))
        chart.legend().setMarkerShape(QLegend.MarkerShapeCircle)
        
        # Set margins and title
        chart.setMargins(QMargins(0, 0, 0, 0))
        chart.setTitle("Crime Type Distribution")
        chart.setTitleFont(QFont("Segoe UI", 12, QFont.Bold))
        
        # Create and configure chart view
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        return chart_view
        
    def create_line_chart(self):
        """Create line chart with real case trends"""
        chart = QChart()
        chart.setBackgroundVisible(False)
        
        # Create series for total and closed cases
        total_series = QSplineSeries()
        total_series.setName("Total Cases")
        
        closed_series = QSplineSeries()
        closed_series.setName("Closed Cases")
        
        try:
            # Get case trends for the last 12 months
            end_date = QDateTime.currentDateTime()
            start_date = end_date.addMonths(-11)
            
            # Get monthly stats
            case_stats = self.case_model.get_case_stats()
            monthly_stats = case_stats.get('monthly_stats', [])
            
            # Process data points
            max_count = 0
            if monthly_stats:
                for stat in monthly_stats:
                    date = QDateTime.fromString(stat['month'], "yyyy-MM")
                    total = int(stat['total_cases'])
                    closed = int(stat['closed_cases'])
                    
                    total_series.append(date.toMSecsSinceEpoch(), total)
                    closed_series.append(date.toMSecsSinceEpoch(), closed)
                    max_count = max(max_count, total, closed)
            
        except Exception as e:
            print(f"Error creating line chart: {str(e)}")
            current_time = QDateTime.currentDateTime().toMSecsSinceEpoch()
            total_series.append(current_time, 0)
            closed_series.append(current_time, 0)
            max_count = 10
        
        # Set line styles
        total_pen = QPen(QColor("#4285f4"))  # Blue for total cases
        total_pen.setWidth(2)
        total_series.setPen(total_pen)
        
        closed_pen = QPen(QColor("#34a853"))  # Green for closed cases
        closed_pen.setWidth(2)
        closed_series.setPen(closed_pen)
        
        # Add series to chart
        chart.addSeries(total_series)
        chart.addSeries(closed_series)
        
        # Setup axes
        axis_x = QDateTimeAxis()
        axis_x.setFormat("MMM yyyy")
        axis_x.setTitleText("")
        axis_x.setLabelsColor(QColor("#5f6368"))
        axis_x.setGridLineColor(QColor("#e0e0e0"))
        axis_x.setLinePen(QPen(QColor("#e0e0e0")))
        axis_x.setLabelsFont(QFont("Segoe UI", 9))
        
        axis_y = QValueAxis()
        # Set range based on actual data with some padding
        y_max = max(max_count + (5 - (max_count % 5)), 10)  # Round up to nearest 5, minimum of 10
        axis_y.setRange(0, y_max)
        axis_y.setTickCount(6)
        axis_y.setLabelFormat("%d")
        axis_y.setTitleText("")
        axis_y.setLabelsColor(QColor("#5f6368"))
        axis_y.setGridLineColor(QColor("#e0e0e0"))
        axis_y.setLinePen(QPen(QColor("#e0e0e0")))
        axis_y.setLabelsFont(QFont("Segoe UI", 9))
        
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        total_series.attachAxis(axis_x)
        total_series.attachAxis(axis_y)
        closed_series.attachAxis(axis_x)
        closed_series.attachAxis(axis_y)
        
        chart.setMargins(QMargins(0, 0, 0, 0))
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        return chart_view
        
    def update_statistics(self):
        """Update statistics cards with real data"""
        try:
            # Get total criminals
            total_criminals = self.criminal_model.count()
            self.stat_cards[0].update_value(str(total_criminals))
            
            # Get case statistics
            total_cases = self.case_model.count()
            open_cases = len(self.case_model.get_cases_by_status('Open'))
            
            self.stat_cards[1].update_value(str(total_cases))
            self.stat_cards[2].update_value(str(open_cases))
            
            # Get total evidence
            total_evidence = self.evidence_model.count()
            self.stat_cards[3].update_value(str(total_evidence))
            
        except Exception as e:
            print(f"Error updating statistics: {str(e)}")
            # Set default values in case of error
            default_values = ["0", "0", "0", "0"]
            for card, value in zip(self.stat_cards, default_values):
                card.update_value(value)
                
    def refresh(self):
        """Refresh all dashboard data"""
        # Update statistics first
        self.update_statistics()
        
        # Then update charts
        charts_section = self.findChild(QFrame, "charts-section")
        if charts_section:
            # Clear existing charts
            for i in reversed(range(charts_section.layout().count())): 
                charts_section.layout().itemAt(i).widget().setParent(None)
            
            # Create new charts
            self.create_charts(charts_section.layout())

    def showEvent(self, event):
        """Handle show event"""
        super().showEvent(event)
        self.refresh()
        
    def hideEvent(self, event):
        """Handle hide event"""
        super().hideEvent(event)
        
    def closeEvent(self, event):
        super().closeEvent(event)
        self.refresh_timer.stop()

    def create_stat_cards(self, layout):
        """Create statistics cards"""
        self.stat_cards = []
        
        # Card configurations with proper colors
        cards = [
            ("Total Criminals", "0", "criminal", "#1a73e8"),  # Blue
            ("Total Cases", "0", "case", "#34a853"),         # Green
            ("Open Cases", "0", "case", "#ea4335"),          # Red
            ("Total Evidence", "0", "evidence", "#fbbc05")   # Yellow
        ]
        
        # Create container for cards
        cards_container = QFrame()
        cards_container.setObjectName("cardsContainer")
        cards_layout = QHBoxLayout(cards_container)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(20)
        
        for title, value, icon, color in cards:
            card = StatCard(title, value, f"assets/icons/{icon}.svg", color)
            cards_layout.addWidget(card)
            self.stat_cards.append(card)
        
        # Add stretch to ensure cards are evenly spaced
        cards_layout.addStretch()
        layout.addWidget(cards_container)
        
        # Style the container
        cards_container.setStyleSheet("""
            #cardsContainer {
                background: transparent;
            }
        """)

    def create_charts(self, layout):
        """Create charts section"""
        # Create pie chart container
        pie_container = QFrame()
        pie_container.setObjectName("chart-container")
        pie_layout = QVBoxLayout(pie_container)
        pie_layout.setContentsMargins(20, 20, 20, 20)
        pie_layout.setSpacing(10)
        
        pie_title = QLabel("Crime Types Distribution")
        pie_title.setObjectName("chart-title")
        pie_layout.addWidget(pie_title)
        
        self.pie_chart = self.create_pie_chart()
        pie_layout.addWidget(self.pie_chart)
        layout.addWidget(pie_container)
        
        # Create line chart container
        line_container = QFrame()
        line_container.setObjectName("chart-container")
        line_layout = QVBoxLayout(line_container)
        line_layout.setContentsMargins(20, 20, 20, 20)
        line_layout.setSpacing(10)
        
        # Add header section with title and date range
        header_widget = QFrame()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)
        
        line_title = QLabel("Case Trends")
        line_title.setObjectName("chart-title")
        header_layout.addWidget(line_title)
        
        # Add date range controls
        date_range = QFrame()
        date_range.setObjectName("date-range")
        date_layout = QHBoxLayout(date_range)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(10)
        
        from_label = QLabel("From:")
        from_label.setObjectName("range-label")
        date_layout.addWidget(from_label)
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-11))
        self.date_from.dateChanged.connect(self.refresh)
        date_layout.addWidget(self.date_from)
        
        to_label = QLabel("To:")
        to_label.setObjectName("range-label")
        date_layout.addWidget(to_label)
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.dateChanged.connect(self.refresh)
        date_layout.addWidget(self.date_to)
        
        header_layout.addWidget(date_range)
        header_layout.addStretch()
        
        line_layout.addWidget(header_widget)
        
        self.line_chart = self.create_line_chart()
        line_layout.addWidget(self.line_chart)
        layout.addWidget(line_container)
        
        # Add styles for date range
        self.setStyleSheet(self.styleSheet() + """
            #date-range {
                background: transparent;
            }
            #range-label {
                color: #5f6368;
                font-size: 14px;
            }
            QDateEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 120px;
                color: #202124;
                background: white;
            }
            QDateEdit::drop-down {
                border: none;
                width: 20px;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #5f6368;
                margin-top: 2px;
            }
        """) 