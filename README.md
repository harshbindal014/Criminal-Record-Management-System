# Crime Record Management System

A professional desktop application for managing criminal records, cases, and evidence, built with PyQt5 and SQLite.

## Features

- Modern dark-themed user interface
- Secure user authentication system
- Comprehensive criminal record management
- Case tracking and management
- Evidence management with image support
- Advanced reporting and analytics
- Data export in Excel and PDF formats
- Customizable settings

## System Requirements

- Python 3.8 or higher
- Windows/Linux/macOS

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/crime-record-system.git
cd crime-record-system
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python scripts/init_db.py
```

## Running the Application

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Run the application:
```bash
python main.py
```

## Default Login Credentials

- Username: admin
- Password: admin123

*Please change these credentials after first login*

## Project Structure

```
crime_record_system/
├── assets/
│   ├── icons/
│   └── images/
├── models/
│   ├── case.py
│   ├── criminal.py
│   ├── evidence.py
│   └── user.py
├── ui/
│   ├── pages/
│   ├── styles/
│   └── widgets/
├── utils/
│   ├── db_helper.py
│   ├── export_helper.py
│   └── image_helper.py
├── scripts/
│   └── init_db.py
├── main.py
├── requirements.txt
└── README.md
```

## Features in Detail

### Criminal Management
- Add, edit, and delete criminal records
- Upload and manage criminal photos
- Track criminal history and status
- Link criminals to cases

### Case Management
- Create and manage case files
- Assign officers to cases
- Track case status and progress
- Link criminals and evidence to cases

### Evidence Management
- Record and track physical/digital evidence
- Upload evidence photos
- Manage chain of custody
- Link evidence to cases

### Reporting
- Generate various reports:
  - Case status reports
  - Criminal statistics
  - Evidence inventory
  - Chain of custody reports
- Export reports in Excel or PDF format

### Settings
- User preferences
- Display settings
- Data refresh settings
- Export preferences

## Security Features

- Password hashing using bcrypt
- Role-based access control
- Secure image storage
- Activity logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team. 