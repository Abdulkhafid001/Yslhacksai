"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoBase(BaseModel):
    """Shared fields for creating and updating to-dos."""

    title: str = Field(..., min_length=1, max_length=255, examples=["Buy groceries"])
    description: str | None = Field(
        default=None, max_length=2000, examples=["Milk, eggs, bread and coffee"]
    )
    completed: bool = Field(default=False, examples=[False])


class TodoCreate(TodoBase):
    """Payload for creating a to-do item."""


class TodoUpdate(BaseModel):
    """Payload for updating a to-do item (all fields optional)."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool | None = Field(default=None)


class TodoRead(TodoBase):
    """To-do item as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class TodoList(BaseModel):
    """Paginated list of to-do items."""

    items: list[TodoRead]
    total: int
    limit: int
    offset: int
