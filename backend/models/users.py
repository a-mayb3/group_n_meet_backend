from pydantic import BaseModel

class UserBase(BaseModel):
    id: str
    email_address: str
    display_name: str
    user_type: str # REGULAR or ADMIN


class UserAuth(BaseModel):
    email_address: str
    password: str
