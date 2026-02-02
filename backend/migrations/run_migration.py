"""Run migration against Railway database."""
import os
import psycopg2

def run_migration():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return False

    # Read migration file
    migration_path = os.path.join(os.path.dirname(__file__), "001_create_moirai_predictions.sql")
    with open(migration_path, "r") as f:
        migration_sql = f.read()

    print(f"Connecting to database...")
    conn = psycopg2.connect(database_url)
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            print("Running migration: 001_create_moirai_predictions.sql")
            cur.execute(migration_sql)
            print("Migration completed successfully!")

            # Verify table was created
            cur.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'moirai_predictions'
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()
            print(f"\nTable 'moirai_predictions' created with {len(columns)} columns:")
            for col_name, col_type in columns:
                print(f"  - {col_name}: {col_type}")
        return True
    except Exception as e:
        print(f"Migration failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
