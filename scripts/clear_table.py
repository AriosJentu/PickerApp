import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, inspect, text

from app.core.config import settings
from app.modules.db.base import Base


def clear_tables(tables_to_clear=None, db_url=settings.DATABASE_URL_SYNC):
    engine = create_engine(db_url)

    try:
        with engine.connect() as connection:
            inspector = inspect(engine)

            existing_tables = inspector.get_table_names()

            connection.execute(text("SET session_replication_role = 'replica';"))

            if not tables_to_clear or "all" in tables_to_clear:
                tables_to_clear = [table.name for table in Base.metadata.sorted_tables]

            for table in tables_to_clear:
                if table not in existing_tables:
                    print(f"Table '{table}' does not exist. Skipping.")
                    continue

                safe_table_name = f'"{table}"'
                connection.execute(text(f"TRUNCATE TABLE {safe_table_name} RESTART IDENTITY CASCADE;"))
                print(f"Table '{table}' has been cleared.")

            connection.execute(text("SET session_replication_role = 'origin';"))

        print("Database clearing completed.")
    except Exception as e:
        print(f"Error occurred while clearing tables: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Database Tables Cleaner.")
    parser.add_argument(
        "--base",
        choices=["main", "test"],
        default="main",
        help="Choose the database to clean: 'main' or 'test'.",
    )
    parser.add_argument(
        "--tables",
        nargs="*",
        default=None,
        help="List of tables to clear. Use 'all' to clear all available tables.",
    )

    args = parser.parse_args()
    db_mapping = {"main": settings.DATABASE_URL_SYNC, "test": settings.DATABASE_URL_TEST_SYNC}

    if db_url := db_mapping.get(args.base):
        clear_tables(args.tables, db_url)
    else:
        print("Invalid database selection. Use 'main' or 'test'.")