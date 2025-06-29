from pydantic import BaseModel

class BlogSchema(BaseModel):
    id: int
    title: str
    content: str

    # Pydantic V2 新配置写法，替换旧的 orm_mode
    model_config = {
        "from_attributes": True
    }

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str