"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Wedding site schemas

class Event(BaseModel):
    """
    Event details for the wedding website.
    Collection name: "event"
    """
    couple_names: str = Field(..., description="Names of the couple")
    date: str = Field(..., description="Date of the wedding, e.g., 2026-05-10")
    city: str = Field(..., description="City and province")
    church_name: str = Field(..., description="Church name")
    church_address: str = Field(..., description="Full church address")
    venue_name: str = Field(..., description="Reception venue name")
    venue_address: str = Field(..., description="Reception venue address")
    notes: Optional[str] = Field(None, description="Extra notes shown on the homepage")

class Place(BaseModel):
    """
    Generic place (hairdresser, barber, hotel, restaurant, cultural POI, etc.)
    Collection name: "place"
    """
    category: str = Field(..., description="One of: church, venue, hairdresser, barber, hotel, restaurant, poi")
    name: str = Field(..., description="Place name")
    address: str = Field(..., description="Full address")
    description: Optional[str] = Field(None, description="Short description or tips")
    phone: Optional[str] = Field(None, description="Phone number")
    website: Optional[str] = Field(None, description="Website URL as string")
    maps_url: Optional[str] = Field(None, description="Google Maps link")
    tags: Optional[List[str]] = Field(default=None, description="Optional tags/labels")
