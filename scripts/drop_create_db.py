import os
from dotenv import load_dotenv

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "picker_app")
DB_NAME_TEST = os.getenv("DB_NAME_TEST", "picker_app_test")


def create_database(db_name):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database="postgres"
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor = connection.cursor()

        try:
            cursor.execute(f"CREATE DATABASE {db_name};")
            print(f"Database '{db_name}' created successfully.")
        except psycopg2.errors.DuplicateDatabase:
            print(f"Database '{db_name}' already exists.")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"Error: {e}")


def drop_database(db_name):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database="postgres"
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor = connection.cursor()

        try:
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
            print(f"Database '{db_name}' dropped successfully.")
        except Exception as e:
            print(f"Error while dropping database: {e}")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage PostgreSQL databases.")
    parser.add_argument(
        "--create",
        choices=["main", "test"],
        help="Create the main or test database.",
    )
    parser.add_argument(
        "--drop",
        choices=["main", "test"],
        help="Drop the main or test database.",
    )

    args = parser.parse_args()
    mapping = {"main": DB_NAME, "test": DB_NAME_TEST}

    if args.create and (name := mapping.get(args.create, 0)) != 0:
        create_database(name)
    elif args.drop and (name := mapping.get(args.drop, 0)) != 0:
        drop_database(name)
    else:
        print("No action specified. Use --create or --drop with 'main' or 'test'.")
