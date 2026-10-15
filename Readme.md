# Healthcare Data Migration Project

## Project Overview
This project demonstrates a simple healthcare data migration pipeline using Python and PostgreSQL. Patient records are read from a CSV file, validated, and loaded into a PostgreSQL database.

## Technologies Used
- Python
- PostgreSQL
- SQL
- CSV
- Psycopg

## Project Workflow
1. Read patient data from a source CSV file.
2. Validate required fields such as patient ID, first name, last name, and phone number.
3. Identify duplicate patient IDs.
4. Load valid records into PostgreSQL.
5. Verify target record counts.
6. Perform source-to-target reconciliation checks.

## Data Validation Rules
A record is considered valid when the following fields are present:
- Patient ID
- First name
- Last name
- Phone number

Records that fail these checks are excluded from the load.

## Database Details
**Database:** `healthcare_migration`

**Target table:** `public.patients`

| Column | Description |
|---|---|
| patient_id | Unique patient identifier |
| first_name | Patient's first name |
| last_name | Patient's last name |
| dob | Date of birth |
| gender | Gender |
| phone | Phone number |

## Project Structure
```text
Healthcare_Data_Migration/
├── data/
│   └── patients_source.csv
├── output/
├── src/
│   ├── migration.py
│   ├── load_to_postgres.py
│   └── test_connection.py
└── README.md
```

## How to Run

1. Install Python and PostgreSQL.
2. Install the PostgreSQL Python driver:

   ```bash
   python -m pip install "psycopg[binary]"
   ```

3. Set the PostgreSQL password in PowerShell:

   ```powershell
   $env:PGPASSWORD = Read-Host "PostgreSQL password"
   ```

4. Run the migration script from the project folder:

   ```powershell
   python src/load_to_postgres.py
   ```

## Reconciliation
The script checks:
- Source record count
- Valid record count
- Rejected record count
- Target record count
- Source and target reconciliation status

## Learning Outcomes
- CSV processing using Python
- Data quality validation
- Duplicate ID detection
- PostgreSQL connectivity
- SQL-based record verification
- Data migration reconciliation

## Future Improvements
- Export rejected records to an error report
- Add automated tests
- Improve duplicate record handling
- Add logging and detailed migration reports
