"""FastAPI application entry point with to-do list CRUD endpoints."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import __version__, crud, models, schemas
from .database import engine, get_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Create database tables on application startup."""
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="To-Do List API",
    description=(
        "A simple FastAPI application for managing a to-do list with full "
        "CRUD capabilities: create, read, update and delete tasks."
    ),
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    """Root endpoint with a friendly message."""
    return {"message": "Welcome to the To-Do List API", "docs": "/docs"}


@app.get("/health", tags=["health"], summary="Health check")
def health_check() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get(
    "/todos",
    response_model=schemas.TodoList,
    tags=["todos"],
    summary="List to-do items",
)
def list_todos(
    completed: bool | None = Query(
        default=None, description="Filter by completion status"
    ),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> schemas.TodoList:
    """Return a paginated list of to-do items, optionally filtered."""
    items, total = crud.list_todos(db, completed=completed, limit=limit, offset=offset)
    return schemas.TodoList(
        items=items, total=total, limit=limit, offset=offset
    )


@app.get(
    "/todos/{todo_id}",
    response_model=schemas.TodoRead,
    tags=["todos"],
    summary="Get a to-do item",
)
def get_todo(todo_id: int, db: Session = Depends(get_db)) -> models.Todo:
    """Return a single to-do item by id."""
    db_todo = crud.get_todo(db, todo_id)
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"To-do item {todo_id} not found",
        )
    return db_todo


@app.post(
    "/todos",
    response_model=schemas.TodoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["todos"],
    summary="Create a to-do item",
)
def create_todo(
    todo: schemas.TodoCreate, db: Session = Depends(get_db)
) -> models.Todo:
    """Create a new to-do item."""
    return crud.create_todo(db, todo)


@app.put(
    "/todos/{todo_id}",
    response_model=schemas.TodoRead,
    tags=["todos"],
    summary="Update a to-do item",
)
def update_todo(
    todo_id: int,
    todo: schemas.TodoUpdate,
    db: Session = Depends(get_db),
) -> models.Todo:
    """Replace or update fields of an existing to-do item."""
    db_todo = crud.get_todo(db, todo_id)
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"To-do item {todo_id} not found",
        )
    return crud.update_todo(db, db_todo, todo)


@app.patch(
    "/todos/{todo_id}",
    response_model=schemas.TodoRead,
    tags=["todos"],
    summary="Partially update a to-do item",
)
def patch_todo(
    todo_id: int,
    todo: schemas.TodoUpdate,
    db: Session = Depends(get_db),
) -> models.Todo:
    """Partially update an existing to-do item (e.g. toggle completion)."""
    db_todo = crud.get_todo(db, todo_id)
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"To-do item {todo_id} not found",
        )
    return crud.update_todo(db, db_todo, todo)


@app.delete(
    "/todos/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["todos"],
    summary="Delete a to-do item",
)
def delete_todo(todo_id: int, db: Session = Depends(get_db)) -> Response:
    """Delete a to-do item by id."""
    db_todo = crud.get_todo(db, todo_id)
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"To-do item {todo_id} not found",
        )
    crud.delete_todo(db, db_todo)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
