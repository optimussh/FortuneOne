from typing import Optional
from sqlmodel import SQLModel, Field

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    slug: str = Field(unique=True, index=True)
    icon: str = ""  # emoji or icon name

class CategoryRead(SQLModel):
    id: int
    name: str
    slug: str
    icon: str
