"""
Database Schemas for the E‑Gifts premium store

Each Pydantic model corresponds to a MongoDB collection. The collection name is the
lowercase class name.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

class Gift(BaseModel):
    """
    Collection: gift
    Digital gifts like mini‑games, Telegram mini‑bots, reminders, love notes, etc.
    """
    title: str = Field(..., max_length=120)
    slug: str = Field(..., max_length=140, description="URL-friendly unique id")
    tagline: Optional[str] = Field(None, max_length=200)
    description: str = Field(..., max_length=2000)
    price: float = Field(..., ge=0)
    badge: Optional[str] = Field(None, description="Small highlight badge, e.g. 'New' or 'Best Seller'")
    category: str = Field(..., description="e.g. games, reminders, notes")
    cover: Optional[str] = Field(None, description="Hero image/illustration URL")
    gallery: Optional[List[str]] = Field(default_factory=list)
    features: Optional[List[str]] = Field(default_factory=list)
    rating: Optional[float] = Field(4.8, ge=0, le=5)

class OrderItem(BaseModel):
    gift_slug: str
    title: str
    price: float
    quantity: int = Field(1, ge=1, le=10)

class Customer(BaseModel):
    name: str
    email: EmailStr
    note_for_recipient: Optional[str] = None
    recipient_handle: Optional[str] = Field(None, description="@telegram or any contact hint")

class Order(BaseModel):
    """
    Collection: order
    Stores a placed order with items and buyer information. Fulfillment is manual in this demo.
    """
    items: List[OrderItem]
    customer: Customer
    total: float = Field(..., ge=0)
    status: str = Field("pending", description="pending | paid | delivered | cancelled")

class Testimonial(BaseModel):
    """Collection: testimonial"""
    author: str
    role: Optional[str] = None
    content: str
    avatar: Optional[str] = None
    rating: Optional[float] = Field(5.0, ge=0, le=5)
