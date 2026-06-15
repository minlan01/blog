from pydantic import BaseModel, Field


class CategoryRead(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None = None

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r'^[a-zA-Z0-9][a-zA-Z0-9\-_]*$')
    description: str | None = Field(default=None, max_length=255)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    slug: str | None = Field(default=None, min_length=1, max_length=100, pattern=r'^[a-zA-Z0-9][a-zA-Z0-9\-_]*$')
    description: str | None = Field(default=None, max_length=255)
