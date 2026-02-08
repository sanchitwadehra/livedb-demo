"""SQLAlchemy models — used for write operations."""

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

_dir = os.path.dirname(os.path.abspath(__file__))
DB_URL = f"sqlite:///{os.path.join(_dir, 'app.sqlite')}"

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="active")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    created_at = Column(String, nullable=False)
