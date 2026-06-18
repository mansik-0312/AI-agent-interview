from pydantic import BaseModel, EmailStr
from typing import List, Optional

class EmailRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
    cc: Optional[List[EmailStr]] = []
    bcc: Optional[List[EmailStr]] = []
    attachments: Optional[List[str]] = []
    is_html: bool = True