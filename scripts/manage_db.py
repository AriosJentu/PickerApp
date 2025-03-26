import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import asyncio

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import IntegrityError

from app.core.config import settings

from app.dependencies.database import get_async_session

from app.core.base.base import Base
from app.modules.auth.user.schemas import UserUpdate
from app.modules.auth.user.enums import UserRole
from app.modules.auth.user.services.user import UserService


def get_url_from_type(db_name: str = "main") -> str:
    if db_name == "main":
        return settings.DATABASE_URL_SYNC
    return settings.DATABASE_URL_TEST_SYNC


def get_name_from_type(db_name: str = "main") -> str:
    if db_name == "main":
        return settings.DB_NAME
    return settings.DB_NAME_TEST


async def clear_tables(tables: list[str], db_name: str = "main"):

    url = get_url_from_type(db_name)
    print(f"Working with: {url}")
    engine = create_engine(url)
    with engine.connect() as connection:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        if "all" in tables:
            tables = Base.metadata.tables.keys()
        
        connection.execute(text("SET session_replication_role = 'replica';"))
        for table in tables:
            if table not in existing_tables:
                print(f"Table '{table}' does not exist. Skipping.")
                continue

            connection.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE;'))
            print(f"Table '{table}' has been cleared.")

        connection.execute(text("SET session_replication_role = 'origin';"))
        connection.commit()
    
    print("Database table clearing completed.")


def drop_database(db_name: str = "main"):
    base = get_name_from_type(db_name)
    try:
        print(f"Connection info: {settings.DB_USER}, {settings.DB_HOST}:{settings.DB_PORT}, {db_name}:{base}")
        connection = psycopg2.connect(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database="postgres"
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {base};")
            print(f"Database '{base}' dropped successfully.")
        
        connection.close()

    except Exception as e:
        print(f"Error while dropping database '{base}': {e}")


def create_database(db_name: str = "main"):
    base = get_name_from_type(db_name)
    try:
        print(f"Connection info: {settings.DB_USER}, {settings.DB_HOST}:{settings.DB_PORT}, {db_name}:{base}")
        connection = psycopg2.connect(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database="postgres"
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE {base};")
            print(f"Database '{base}' created successfully.")
        
        connection.close()

    except psycopg2.errors.DuplicateDatabase:
        print(f"Database '{base}' already exists.")

    except Exception as e:
        print(f"Error while creating database '{base}': {e}")


async def init_db(db_name: str = "main"):
    url = get_url_from_type(db_name)
    print(f"Working with: {url}")
    engine = create_engine(url)

    print(f"Creating tables in database '{db_name}'...")
    Base.metadata.create_all(bind=engine)
    print(f"Tables in database '{db_name}' created.")


async def create_admin():
    
    session = get_async_session()
    async for session in get_async_session():
        admin_data = UserUpdate(username="admin", email=settings.ADMIN_EMAIL, password=settings.ADMIN_PASSWORD, role=UserRole.ADMIN)
        service = UserService(session)
        try:
            await service.create(admin_data)
            print("Administrator successfully created.")

        except IntegrityError as e:
            print(f"Problem with creating administrator: User already exists")
        
        except Exception as e:
            print(f"Problem with creating administrator: {e}")


def parse_args():
    parser = argparse.ArgumentParser(description="Database management utility.")

    parser.add_argument("--db", choices=["main", "test"], default="main", help="Select the database (default: main)")
    parser.add_argument("--clear-table", nargs="+", help="Clears one or more tables (or 'all' for all tables)")
    parser.add_argument("--drop", action="store_true", help="Drops the selected database")
    parser.add_argument("--create", action="store_true", help="Creates the selected database")
    parser.add_argument("--init", action="store_true", help="Creates tables in the selected database")
    parser.add_argument("--create-admin", action="store_true", help="Creates an admin user in the selected database")

    return parser.parse_args()


async def main():
    args = parse_args()
    db_name = args.db

    if args.clear_table:
        await clear_tables(args.clear_table, db_name)
    elif args.drop:
        drop_database(db_name)
    elif args.create:
        create_database(db_name)
    elif args.init:
        await init_db(db_name)
    elif args.create_admin:
        await create_admin()
    else:
        print("No arguments provided. Run with --help for usage information.")

if __name__ == "__main__":
    asyncio.run(main())