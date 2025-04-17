import pandas as pd
from models.case import CaseModel
from models.criminal import CriminalModel
from models.evidence import EvidenceModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataImporter:
    def __init__(self):
        self.case_model = CaseModel()
        self.criminal_model = CriminalModel()
        self.evidence_model = EvidenceModel()

    def import_data(self, file_path, data_type):
        """Import data from Excel or CSV file into the database."""
        try:
            # Determine file type and read accordingly
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format. Please use CSV or Excel files.")

            # Process data based on type
            if data_type == 'cases':
                return self._import_cases(df)
            elif data_type == 'case_criminals':
                return self._import_case_criminals(df)
            elif data_type == 'evidence':
                return self._import_evidence(df)
            else:
                raise ValueError("Invalid data type specified")

        except Exception as e:
            logger.error(f"Error importing data: {str(e)}")
            raise

    def _import_cases(self, df):
        """Import cases from DataFrame with criminal relationships."""
        required_columns = ['title', 'description', 'status', 'priority', 'criminal_ids']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(
                "Missing required columns for cases import.\n"
                "Required columns: title, description, status, priority, criminal_ids\n"
                "Note: criminal_ids should be comma-separated list of criminal IDs"
            )

        success_count = 0
        error_count = 0

        for _, row in df.iterrows():
            try:
                # First, verify that all referenced criminals exist
                criminal_ids = [int(id.strip()) for id in str(row['criminal_ids']).split(',') if id.strip()]
                for criminal_id in criminal_ids:
                    if not self.criminal_model.get_criminal(criminal_id):
                        raise ValueError(f"Criminal ID {criminal_id} does not exist")

                # Create the case
                case_data = {
                    'title': row['title'],
                    'description': row['description'],
                    'status': row['status'],
                    'priority': row['priority'],
                    'date_opened': datetime.now().strftime('%Y-%m-%d'),
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                }
                case_id = self.case_model.create_case(case_data, criminal_ids)

                success_count += 1
            except Exception as e:
                logger.error(f"Error importing case: {str(e)}")
                error_count += 1

        return success_count, error_count

    def _import_case_criminals(self, df):
        """Import criminal data and automatically create/update cases."""
        required_columns = [
            'name', 'age', 'gender', 'nationality', 'case_title', 
            'case_description', 'case_status', 'case_priority'
        ]
        if not all(col in df.columns for col in required_columns):
            raise ValueError(
                "Missing required columns for case-criminal import.\n"
                "Required: name, age, gender, nationality, case_title, "
                "case_description, case_status, case_priority"
            )

        success_count = 0
        error_count = 0

        for _, row in df.iterrows():
            try:
                # First create/update the criminal
                criminal_data = {
                    'name': row['name'],
                    'age': int(row['age']),
                    'gender': row['gender'],
                    'nationality': row['nationality'],
                    'status': row.get('status', 'Active'),
                    'description': row.get('description', ''),
                    'date_added': datetime.now().strftime('%Y-%m-%d')
                }
                criminal_id = self.criminal_model.add_criminal(criminal_data)

                # Then create the case and link it
                case_data = {
                    'title': row['case_title'],
                    'description': row['case_description'],
                    'status': row['case_status'],
                    'priority': row['case_priority'],
                    'date_opened': datetime.now().strftime('%Y-%m-%d'),
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                }
                case_id = self.case_model.create_case(case_data)

                # Link the criminal to the case
                self.case_model.link_criminals(case_id, [criminal_id])

                success_count += 1
            except Exception as e:
                logger.error(f"Error importing case-criminal: {str(e)}")
                error_count += 1

        return success_count, error_count

    def _import_evidence(self, df):
        """Import evidence with case relationships."""
        required_columns = ['name', 'type', 'description', 'case_id', 'location']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(
                "Missing required columns for evidence import.\n"
                "Required: name, type, description, case_id, location\n"
                "Note: case_id must reference an existing case"
            )

        success_count = 0
        error_count = 0

        for _, row in df.iterrows():
            try:
                # Verify the case exists
                case_id = int(row['case_id'])
                if not self.case_model.get_case(case_id):
                    raise ValueError(f"Case ID {case_id} does not exist")

                evidence_data = {
                    'name': row['name'],
                    'type': row['type'],
                    'description': row['description'],
                    'case_id': case_id,
                    'status': row.get('status', 'Active'),
                    'date_added': datetime.now().strftime('%Y-%m-%d'),
                    'location': row['location']
                }
                self.evidence_model.add_evidence(evidence_data)
                success_count += 1
            except Exception as e:
                logger.error(f"Error importing evidence: {str(e)}")
                error_count += 1

        return success_count, error_count

    def get_import_template(self, data_type):
        """Generate a template DataFrame for data import."""
        if data_type == 'cases':
            return pd.DataFrame(columns=[
                'title', 'description', 'status', 'priority', 'criminal_ids'
            ])
        elif data_type == 'case_criminals':
            return pd.DataFrame(columns=[
                'name', 'age', 'gender', 'nationality', 'status', 'description',
                'case_title', 'case_description', 'case_status', 'case_priority'
            ])
        elif data_type == 'evidence':
            return pd.DataFrame(columns=[
                'name', 'type', 'description', 'case_id', 'location', 'status'
            ])
        else:
            raise ValueError("Invalid template type") 