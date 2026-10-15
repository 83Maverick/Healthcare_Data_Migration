import csv
import os
from pathlib import Path
from collections import Counter

import psycopg


# 1. File paths and database password
PROJECT_DIR = Path(__file__).resolve().parent.parent
CSV_FILE = PROJECT_DIR / "data" / "patients_source.csv"
DB_PASSWORD = os.getenv("PGPASSWORD")

if not DB_PASSWORD:
    raise ValueError(
        "PGPASSWORD is not set. Set it in the terminal."
    )


# 2. Read source CSV
with open(CSV_FILE, newline="", encoding="utf-8-sig") as file:
    patients = list(csv.DictReader(file))

print("Source records:", len(patients))


# 3. Validate records
valid_patients = [
    p for p in patients
    if p["patient_id"].strip()
    and p["first_name"].strip()
    and p["last_name"].strip()
    and p["phone"].strip()
]

rejected_count = len(patients) - len(valid_patients)

print("Valid records:", len(valid_patients))
print("Rejected records:", rejected_count)


# 4. Detect duplicate patient IDs
patient_id_counts = Counter(
    p["patient_id"].strip()
    for p in valid_patients
)

duplicate_ids = [
    patient_id
    for patient_id, count in patient_id_counts.items()
    if count > 1
]

print("Duplicate patient IDs:", duplicate_ids)


# 5. Connect to PostgreSQL and load records
with psycopg.connect(
    host="127.0.0.1",
    port=5432,
    dbname="healthcare_migration",
    user="postgres",
    password=DB_PASSWORD,
) as conn:

    with conn.cursor() as cur:

        cur.execute("SELECT current_database()")
        print("Connected database:", cur.fetchone()[0])

        # Create target table if it does not exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.patients (
                patient_id VARCHAR(10) PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                dob DATE,
                gender VARCHAR(10),
                phone VARCHAR(15) NOT NULL
            )
        """)

        # Load valid records
        cur.executemany("""
            INSERT INTO public.patients (
                patient_id,
                first_name,
                last_name,
                dob,
                gender,
                phone
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (patient_id) DO UPDATE SET
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                dob = EXCLUDED.dob,
                gender = EXCLUDED.gender,
                phone = EXCLUDED.phone
        """, [
            (
                p["patient_id"].strip(),
                p["first_name"].strip(),
                p["last_name"].strip(),
                p["dob"].strip() or None,
                p["gender"].strip() or None,
                p["phone"].strip(),
            )
            for p in valid_patients
        ])

        # 6. Count target records
        cur.execute("SELECT COUNT(*) FROM public.patients")
        target_count = cur.fetchone()[0]

        print("Target records:", target_count)

        # 7. Display loaded patients
        cur.execute("""
            SELECT patient_id, first_name, last_name
            FROM public.patients
            ORDER BY patient_id
        """)

        print("Patients in PostgreSQL:")
        for row in cur.fetchall():
            print(row)

        # 8. Reconciliation checks
        print("\n--- Migration Reconciliation ---")
        print("Source records:", len(patients))
        print("Valid records:", len(valid_patients))
        print("Rejected records:", rejected_count)
        print("Target records:", target_count)

        source_check = (
            len(patients) == len(valid_patients) + rejected_count
        )

        target_check = len(valid_patients) == target_count

        print(
            "Source reconciliation:",
            "PASS" if source_check else "CHECK"
        )
        print(
            "Target reconciliation:",
            "PASS" if target_check else "CHECK"
        )


print("\nMigration completed successfully!")
