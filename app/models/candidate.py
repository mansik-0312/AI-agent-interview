from beanie import Document
from pydantic import EmailStr, Field, BaseModel, ConfigDict
from typing import Optional, Dict
from datetime import datetime
from bson import ObjectId


class DeletedInfo(BaseModel):
    status: bool = False
    at: Optional[int] = None
    by: Optional[ObjectId] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Candidate(Document):
    name: str
    email: EmailStr
    mobile: Optional[int] = None
    role: Optional[str] = None
    linkedin_url: Optional[str] = None
    experience: Optional[str] = Field(default=None, description="Experience in years or text format")
    updated_by: Optional[ObjectId] = None
    created_by: Optional[ObjectId] = None
    deleted: DeletedInfo = Field(default_factory=DeletedInfo)

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    class Settings:
        name = "candidates"