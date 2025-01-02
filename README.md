Using on Python 3.13 VENV (Anaconda)

```zsh
pip install -r requirements.txt
```

```zsh
python -m alembic init alembic
```

```zsh
python -m pytest
```

```zsh
python -m uvicorn app.main:app --reload
```

Migrations:
```zsh
python -m alembic revision --autogenerate -m "Changes description"
python -m alembic upgrade head
```
Migrations downgrade:
```zsh
python -m alembic downgrade <revision_id>
```
Revision History (with IDs):
```zsh
python -m alembic history
```

Clean tables:
```zsh
python scripts/drop_create_db.py --drop main
python scripts/drop_create_db.py --create main
python -m alembic stamp head
```