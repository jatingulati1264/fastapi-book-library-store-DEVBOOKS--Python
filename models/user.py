from pydantic import BaseModel, Field
from datetime import datetime

class Register_User(BaseModel):
    user_id: str
    user_name: str = Field(min_length=30)
    user_email: str = Field(min_length=10)
    user_password: str = Field(min_length=10)
    user_type: str
    token: str
    user_created_at: datetime = Field(default_factory=datetime.utcnow)

class Updated_User(BaseModel):
    user_name: str = Field(..., min_length=2)
    user_email: str = Field(min_length=10)
    user_password: str = Field(min_length=10)
    user_created_at: datetime = Field(default_factory=datetime.utcnow)
    user_updated_at: datetime = Field(default_factory=datetime.utcnow)
