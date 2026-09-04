# Yslhacksai
Testing Arena.ai agent mode

# To-Do List API

A simple **FastAPI** application that provides full **CRUD** operations for a to-do list, backed by SQLAlchemy + SQLite.

## Features

- ✅ **Create** a to-do item
- 📖 **Read** (list with filtering/pagination) and get a single item
- ✏️ **Update** (full via `PUT` or partial via `PATCH`)
- 🗑️ **Delete** a to-do item
- 📄 Automatic interactive docs at `/docs` (Swagger UI) and `/redoc`
- 🩺 `/health` endpoint
- 🔒 Input validation with Pydantic
- 💾 Persistent storage in a local SQLite file (`todos.db`)

## Project structure

```
├── app/
│   ├── __init__.py      # Package metadata
│   ├── database.py      # SQLAlchemy engine / session
│   ├── models.py        # ORM model (Todo)
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── crud.py          # Database CRUD helpers
│   └── main.py          # FastAPI app + endpoints
├── requirements.txt
└── README.md
```

## Setup

```bash
# 1. Create and activate a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at <http://localhost:8000> and interactive docs at <http://localhost:8000/docs>.

## API endpoints

| Method   | Endpoint          | Description                                  |
| -------- | ----------------- | -------------------------------------------- |
| `GET`    | `/`               | Welcome message                              |
| `GET`    | `/health`         | Health check                                 |
| `GET`    | `/todos`          | List to-dos (`?completed=true&limit=10&offset=0`) |
| `GET`    | `/todos/{id}`     | Get one to-do by id                          |
| `POST`   | `/todos`          | Create a to-do                               |
| `PUT`    | `/todos/{id}`     | Replace/update a to-do                       |
| `PATCH`  | `/todos/{id}`     | Partially update a to-do                     |
| `DELETE` | `/todos/{id}`     | Delete a to-do                               |

## Example usage

```bash
# Create a to-do
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'


# List all to-dos
curl http://localhost:8000/todos

# Get one to-do
curl http://localhost:8000/todos/1

# Mark as completed (partial update)
curl -X PATCH http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Update (full)
curl -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Organic milk, eggs, bread", "completed": false}'

# Delete
curl -X DELETE http://localhost:8000/todos/1
```

## Request/response schema

A to-do item looks like this:

```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-09-04T08:00:00Z",
  "updated_at": "2026-09-04T08:00:00Z"
}
```

## Running tests

Add `pytest` and `httpx` to your environment, then:

```bash
pytest
```
