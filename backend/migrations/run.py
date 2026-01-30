"""
Simple migration runner for SQL files.
"""

import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_database_url() -> str:
    """Get database URL from environment."""
    url = os.getenv("DATABASE_URL")
    if not url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    # Convert postgres:// to postgresql:// for psycopg2
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def run_migrations() -> None:
    """Run all SQL migration files in order."""
    migrations_dir = Path(__file__).parent
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("No migration files found")
        return

    database_url = get_database_url()
    print(f"Connecting to database...")

    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cursor = conn.cursor()

    # Create migrations tracking table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT NOW()
        )
    """)

    for migration_file in migration_files:
        filename = migration_file.name

        # Check if already applied
        cursor.execute(
            "SELECT 1 FROM _migrations WHERE filename = %s",
            (filename,)
        )
        if cursor.fetchone():
            print(f"  SKIP: {filename} (already applied)")
            continue

        # Read and execute migration
        print(f"  APPLYING: {filename}")
        sql = migration_file.read_text()

        try:
            cursor.execute(sql)
            # Record migration
            cursor.execute(
                "INSERT INTO _migrations (filename) VALUES (%s)",
                (filename,)
            )
            print(f"  SUCCESS: {filename}")
        except Exception as e:
            print(f"  ERROR: {filename} - {e}")
            conn.rollback()
            cursor.close()
            conn.close()
            sys.exit(1)

    cursor.close()
    conn.close()
    print("Migrations complete!")


if __name__ == "__main__":
    run_migrations()
