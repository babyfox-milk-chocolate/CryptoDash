from pydantic import BaseModel, ConfigDict


class WathlistAdd(BaseModel):
    coin_id: str


class WatchlistItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    coin_id: str
    