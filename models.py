from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

# Association table for movie-genre many-to-many relationship
movie_genre = Table('movie_genre', Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id')),
    Column('genre_id', Integer, ForeignKey('genres.id'))
)

class Movie(Base):
    __tablename__ = 'movies'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    year = Column(Integer)
    genres = relationship('Genre', secondary=movie_genre, back_populates='movies')

class Genre(Base):
    __tablename__ = 'genres'
    
    id = Column(Integer, primary_key=True)
    genre_name = Column(String, nullable=False)
    movies = relationship('Movie', secondary=movie_genre, back_populates='genres')

class Tag(Base):
    __tablename__ = 'tags'
    
    tag_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    tag = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

class Link(Base):
    __tablename__ = 'links'
    
    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    imdb_id = Column(Integer)
    tmdb_id = Column(Integer)

# ...existing code...
class Rating(Base):
    __tablename__ = 'ratings'
    
    rating_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    rating = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
