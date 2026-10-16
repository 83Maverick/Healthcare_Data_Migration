import os
import psycopg

try:
    with psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="postgres",
        user="postgres",
        password=os.getenv("PGPASSWORD"),
        connect_timeout=5,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user")
            print("Connected successfully:", cur.fetchone())

except Exception as error:
    print(type(error).__name__)
    print(error)
