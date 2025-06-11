from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "CoolMarket API"
    API_V1_STR: str = "/api/v1"

settings = Settings() 