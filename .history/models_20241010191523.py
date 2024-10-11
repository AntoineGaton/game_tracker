# models.py

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

# Base class for SQLAlchemy models
Base = declarative_base()

# Define the Game model (represents the games table in PostgreSQL)
class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)  # Unique ID (Primary Key)
    steam_id = Column(Integer, unique=True, nullable=False)  # Steam game ID
    title = Column(String, nullable=False)  # Game title
    status = Column(String, default='Backlog')  # Status (Backlog, Playing, Done)
    hours_played = Column(Float)  # Playtime in hours

# Set up the database connection using SQLAlchemy
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Create the 'games' table in the database
Base.metadata.create_all(engine)
