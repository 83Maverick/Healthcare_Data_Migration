import csv
from pathlib import Path

# Define project paths first
PROJECT_DIR = Path(__file__).resolve().parent.parent
SOURCE_FILE = PROJECT_DIR / "data" / "patients_source.csv"

OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
ERROR_FILE = OUTPUT_DIR / "validation_errors.csv"

print("Healthcare Data Migration")
print("-" * 30)


with open(SOURCE_FILE, mode="r", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    patients = list(reader)

print("Source records:", len(patients))

failed_records = []
for patient in patients:
    errors = []

    if not patient["patient_id"].strip():
        errors.append("Missing patient ID")

    if not patient["first_name"].strip():
        errors.append("Missing first name")

    if not patient["last_name"].strip():
        errors.append("Missing last name")

    if not patient["phone"].strip():
        errors.append("Missing phone")

 
    if errors:
        print(patient["patient_id"], "FAILED:", ", ".join(errors))

        failed_records.append({
            **patient,
            "validation_error": ", ".join(errors)
        })
    else:
        print(patient["patient_id"], "VALID")


if failed_records:
    fieldnames = list(failed_records[0].keys())

    with open(ERROR_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(failed_records)

    print("Error report saved:", ERROR_FILE)
else:
    print("No validation errors found.")

import sqlite3

DATABASE_FILE = OUTPUT_DIR / "healthcare_target.db"

# Keep only records that passed validation
valid_records = [
    patient for patient in patients
    if patient["patient_id"].strip()
    and patient["first_name"].strip()
    and patient["last_name"].strip()
    and patient["phone"].strip()
]

with sqlite3.connect(DATABASE_FILE) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            dob TEXT,
            gender TEXT,
            phone TEXT NOT NULL
        )
    """)

    for patient in valid_records:
        conn.execute("""
            INSERT OR REPLACE INTO patients
            (patient_id, first_name, last_name, dob, gender, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            patient["patient_id"],
            patient["first_name"],
            patient["last_name"],
            patient["dob"],
            patient["gender"],
            patient["phone"]
        ))

print("Valid records loaded:", len(valid_records))
print("Target database:", DATABASE_FILE)

with sqlite3.connect(DATABASE_FILE) as conn:
    target_count = conn.execute(
        "SELECT COUNT(*) FROM patients"
    ).fetchone()[0]

source_count = len(patients)
rejected_count = len(failed_records)

print("\n--- Migration Reconciliation ---")
print("Source records:", source_count)
print("Target records:", target_count)
print("Rejected records:", rejected_count)
print("Accounted records:", target_count + rejected_count)

if source_count == target_count + rejected_count:
    print("Reconciliation: PASSED")
else:
    print("Reconciliation: FAILED")

with sqlite3.connect(DATABASE_FILE) as conn:
    rows = conn.execute("""
        SELECT patient_id, first_name, last_name, phone
        FROM patients
        ORDER BY patient_id
    """).fetchall()

print("\n--- Target Database Records ---")

for row in rows:
    print(row)


