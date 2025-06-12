from pydantic import BaseModel, Field, field_validator


class Instrument_schema(BaseModel):
    name: str = Field(..., title="Name")
    ticker: str = Field(
        ...,
        title="Ticker",
        pattern=r'^[A-Z]{2,10}$',
        examples=["BTC", "MEMCOIN"],
        min_length=2,
        max_length=10
    )