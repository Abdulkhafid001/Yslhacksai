"""CRUD operations for to-do items."""

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from .models import Todo
from .schemas import TodoCreate, TodoUpdate


def get_todo(db: Session, todo_id: int) -> Todo | None:
    """Fetch a single to-do item by id."""
    return db.get(Todo, todo_id)


def list_todos(
    db: Session,
    *,
    completed: bool | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[Todo], int]:
    """List to-do items with optional filtering and pagination."""
    query: Select[tuple[Todo]] = select(Todo)

    count_query = select(func.count(Todo.id))
    if completed is not None:
        query = query.where(Todo.completed == completed)
        count_query = count_query.where(Todo.completed == completed)

    total = db.scalar(count_query) or 0
    items = list(
        db.scalars(
            query.order_by(Todo.created_at.desc(), Todo.id.desc())
            .offset(offset)
            .limit(limit)
        )
    )
    return items, total


def create_todo(db: Session, todo: TodoCreate) -> Todo:
    """Create a new to-do item."""
    db_todo = Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def update_todo(db: Session, db_todo: Todo, todo: TodoUpdate) -> Todo:
    """Update an existing to-do item."""
    data = todo.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_todo, field, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def delete_todo(db: Session, db_todo: Todo) -> None:
    """Delete a to-do item."""
    db.delete(db_todo)
    db.commit()
