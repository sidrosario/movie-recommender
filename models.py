from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime, Table, ForeignKey, Text
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
    director = Column(String)
    overview = Column(Text)
    popularity = Column(Float)
    genres = relationship('Genre', secondary=movie_genre, back_populates='movies')

class Genre(Base):
    __tablename__ = 'genres'
    
    id = Column(Integer, primary_key=True)
    genre_name = Column(String, nullable=False)
    movies = relationship('Movie', secondary=movie_genre, back_populates='genres')

# Movie keywords from the TMDB DB
class Keyword(Base):
    __tablename__ = 'keywords'
    
    keyword_id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    keywords = Column(Text, nullable=False)
class Actor(Base):
    __tablename__ = 'actors'
    
    actor_id = Column(Integer, primary_key=True)
    actor_name = Column(String, nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)

class Link(Base):
    __tablename__ = 'links'
    
    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    imdb_id = Column(Integer)
    tmdb_id = Column(Integer)
    poster_path = Column(String)
