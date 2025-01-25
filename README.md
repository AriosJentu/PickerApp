Using on Python 3.13 VENV (Anaconda)

# Install requirements
```zsh
pip install -r requirements.txt
```

# Initializa data structures
```zsh
python -m alembic init alembic
```

# Tests
```zsh
python -m pytest
```
## With coverage
```zsh
python -m pytest --cov=app --cov-report=html
```

# Start application
```zsh
python -m uvicorn app.main:app --reload
```

# Make all migrations
```zsh
python -m alembic revision --autogenerate -m "Changes description"
python -m alembic upgrade head
```
## Migrations downgrade
```zsh
python -m alembic downgrade <revision_id>
```
## Revision History (with IDs)
```zsh
python -m alembic history
```

## Clean tables and re-migrate
```zsh
python scripts/drop_create_db.py --drop main
python scripts/drop_create_db.py --create main
python -m alembic stamp head
python -m alembic revision --autogenerate -m "Update models"
python -m alembic upgrade head
```
