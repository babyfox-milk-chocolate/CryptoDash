from pydantic import BaseModel, ConfigDict



# ---- входные (то, что принимаем от клиента) ---- 
class UserRegister(BaseModel):
    username: str
    password: str
    email: str | None = None

class UserLogin(BaseModel):
    username: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str


# ----- выходные (то, что отдаем клиенту) ----- 
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True) # разрешает читать из ORM объекта

    id: int
    username: str
    email: str | None

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
