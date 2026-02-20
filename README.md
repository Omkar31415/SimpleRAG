Add a .env file with below details

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=****
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=****
GROQ_API_KEY=gsk_NIawSZkuE***S7Pe24Xaf
```

install requirements by creating venv
commands:
```
python -m venv venv
```

```
pip install -r requirements.txt --force
```
To start application
```
python startup.py
```

**IMPORTANT**
also add pgvector extension for your postgres using https://github.com/pgvector/pgvector without this you cannot index documents.
