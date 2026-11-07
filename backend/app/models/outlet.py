from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(500), nullable=True)
    city = Column(String(100), default="New Delhi")
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    outlets = relationship("Outlet", back_populates="restaurant")

class Outlet(Base):
    __tablename__ = "outlets"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    outlet_type = Column(String(100), nullable=False)  # Rooftop Lounge, Fine Dining, Bar
    cuisine_type = Column(String(255), nullable=False)
    opening_time = Column(String(20), default="17:30")
    closing_time = Column(String(20), default="01:30")
    dress_code = Column(String(255), default="Smart Casual")
    seating_capacity = Column(Integer, default=100)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_popular = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    restaurant = relationship("Restaurant", back_populates="outlets")
    menu_categories = relationship("MenuCategory", back_populates="outlet")
    menu_items = relationship("MenuItem", back_populates="outlet")

class MenuCategory(Base):
    __tablename__ = "menu_categories"

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=False)
    environment = Column(String(10), default="DEMO", index=True)  # DEMO or REAL
    name = Column(String(255), nullable=False)
    display_order = Column(Integer, default=0)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    outlet = relationship("Outlet", back_populates="menu_categories")
    items = relationship("MenuItem", back_populates="category")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("menu_categories.id"), nullable=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=False, index=True)
    environment = Column(String(10), default="DEMO", index=True)  # DEMO or REAL
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    dietary_flags = Column(String(255), default="VEG")  # Comma separated e.g. "VEG,GLUTEN_FREE"
    is_available = Column(Boolean, default=True)
    is_signature = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    outlet = relationship("Outlet", back_populates="menu_items")
    category = relationship("MenuCategory", back_populates="items")
