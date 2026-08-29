from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class Book(BaseModel):
    _id: str        # Attributes whose name has a leading underscore are not treated
                    # as fields by Pydantic, and are not included in the model schema.
                    # Instead, these are converted into a "private attribute"
                    # which is not validated or even set during calls to __init__, model_validate,
                    # etc.
    # Lower the minimum lengths or remove them if you want shorter inputs
    book_title: str = Field(..., min_length=3)  # Changed from 10 to 3
    book_author: str = Field(..., min_length=3)  # Changed from 10 to 3
    book_description: str = Field(..., min_length=5)  # Changed from 100 to 5
    book_available_copies: int
    book_total_copies: int
    book_price: int

    # Here it will take default timestamp of now if the timestamp not provided
    book_created_at: datetime = Field(default_factory=datetime.utcnow)


class CartItem(BaseModel):
    user_id: str  # it tells to which user this cart belongs to.
    book_original_id: str # it will actually store the string version of _id (original)
    book_title: str
    book_author: str
    book_price: int
    quantity: int=1

class Order(BaseModel):
    user_id: str
    order_date: datetime = Field(default_factory=datetime.utcnow)
    items: List[dict]
    total_amount: int
    status: str = "Processing"
    shipping_address: str = "" # Added this field

