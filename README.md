# python_demo_api

Simple FastAPI demo project with a minimal but clean structure and three dummy APIs.

## Project layout

- `app/main.py` – FastAPI app factory and `app` instance
- `app/api/v1/routes_demo.py` – demo router with 3 endpoints
- `app/models/demo.py` – Pydantic models for demo items
- `app/services/demo_service.py` – in-memory data and basic business logic
- `app/core/config.py` – lightweight settings container
- `.venv` – local virtual environment (in workspace root)
- `requirements.txt` – pinned dependencies

## Setup

From the workspace root (`/Users/tericsoft/Documents/Try-outs/roam_test`):

```bash
python3 -m venv .venv
source .venv/bin/activate  # on macOS/Linux
# .venv\\Scripts\\activate  # on Windows PowerShell

pip install -r python_demo_api/requirements.txt
```

## Run the API

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --app-dir python_demo_api
```

The API will be available at `http://127.0.0.1:8000`.

### Dummy endpoints

- `GET /api/v1/items` – list demo items
- `GET /api/v1/items/{item_id}` – get single item
- `POST /api/v1/items` – create a new item (in memory only)

