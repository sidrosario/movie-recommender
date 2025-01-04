from datetime import datetime, timezone
import logging
from typing import Any, Dict, List
import pandas as pd
from sqlalchemy import create_engine, select,func
from sqlalchemy.orm import sessionmaker
from config import CSV_FILES, DB_LOCATION, LOG_FILES
from models import Actor, Base, Keyword, Link, Movie, Genre

def create_logger():
    logger = logging.getLogger(__name__)
    logger.handlers.clear()
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter) 
        logger.addHandler(handler)
    return logger

def init_db(location=DB_LOCATION):
    engine = create_engine(location)
    Base.metadata.create_all(engine)
    
    logger = create_logger()
    logger.info("Database created successfully")

    return engine

def load_data(engine):
    global movie_ratings

    Session = sessionmaker(bind=engine)
    logger = logging.getLogger(__name__)
    with Session() as session:
        try:
            logger.info("Loading movies..")
            load_movies_from_csv(session, CSV_FILES['movies'])
            logger.info("Movies loaded successfully")
            load_keywords_from_csv(session, CSV_FILES['keywords'])
            logger.info("Keywords loaded successfully")
            load_actors_from_csv(session, CSV_FILES['actors'])
            logger.info("Actors loaded successfully")
            load_links_from_csv(session, CSV_FILES['links'])
            logger.info("Links loaded successfully")
        except Exception as e:
            print(f"Error loading data: {e}")

def load_movies_from_csv(session, csv_path):
    """
    Load movies from a CSV file into the database.
    This function reads a CSV file containing movie data, processes each row to extract
    movie details, and adds the movies along with their genres to the database session.
    Args:
        session (Session): The SQLAlchemy session object used to interact with the database.
        csv_path (str): The file path to the CSV file containing movie data.
    Raises:
        FileNotFoundError: If the CSV file does not exist at the specified path.
        pd.errors.EmptyDataError: If the CSV file is empty.
        pd.errors.ParserError: If the CSV file contains parsing errors.
    """
    try:
        df = pd.read_csv(csv_path)
        genre_dict = create_genres(session, df['genres'])
                
        for _, row in df.iterrows():
            movie = Movie(
                id=row['movieId'],
                title=str(row['title']),
                year=int(row['year']) if pd.notna(row['year']) else None,
                director=str(row['director']) if pd.notna(row['director']) else None,
                overview=str(row['overview']) if pd.notna(row['overview']) else None,
                popularity=float(row['popularity']) if pd.notna(row['popularity']) else 0.0
            )
            # Convert genres string to list and handle NaN
            if pd.notna(row['genres']):
                movie_genres = [
                    genre_dict[genre_name] 
                    for genre_name in str(row['genres']).split('|') 
                    if genre_name != '(no genres listed)'
                ]
                movie.genres.extend(movie_genres)

            session.add(movie)
        
        session.commit()
    except FileNotFoundError as e:
        print(f"CSV file not found: {e}")
    except pd.errors.EmptyDataError as e:
        print(f"CSV file is empty: {e}")
    except pd.errors.ParserError as e:
        print(f"Error parsing CSV file: {e}")

def create_genres(session, genre_names):
    # Create genres first
    all_genres = set()
    for genres_combined in genre_names:
        if genres_combined == '(no genres listed)' or type(genres_combined) != str:
            continue
        # print("Movie created1: ",genres_combined)    
        all_genres.update(genres_combined.split('|'))
    
    
    genre_dict = {}
    for genre_name in all_genres:
        genre = Genre(genre_name=genre_name)
        session.add(genre)
        genre_dict[genre_name] = genre
    
    return genre_dict

def load_keywords_from_csv(session, csv_path):
    df = pd.read_csv(csv_path)
    
    for _, row in df.iterrows():
        keyword = Keyword(
            movie_id=row['movie_id'],
            keywords=row['keywords']
        )
        session.add(keyword)

    session.commit()

def load_actors_from_csv(session, csv_path):
    df = pd.read_csv(csv_path)
    
    for _, row in df.iterrows():
        actor = Actor(
            movie_id=row['movie_id'],
            actor_name=row['actor_name']
        )
        session.add(actor)

    session.commit()

def load_links_from_csv(session, csv_path):
    """Load movie links data from CSV file into SQLite database.

    Args:
        session (Session): SQLAlchemy session object
        csv_path (str): Path to the CSV file containing movie links data

    Returns:
        None

    Raises:
        FileNotFoundError: If CSV file does not exist
        pd.errors.EmptyDataError: If CSV file is empty
        SQLAlchemyError: If database operation fails

    Example:
        >>> from sqlalchemy.orm import Session
        >>> session = Session()
        >>> load_links_from_csv(session, 'links.csv')
    
    Notes:
        CSV file should have columns: movieId, imdbId, tmdbId
        IMDB IDs are stored without 'tt' prefix
    """
    df = pd.read_csv(csv_path)
    
    for _, row in df.iterrows():
        # print(row['movieId'],row['poster_path'])
        link = Link(
            movie_id=row['movieId'],
            imdb_id=row['imdbId'],
            tmdb_id=row['tmdbId'],
            poster_path=row['poster_path']
        )
        session.add(link)

    session.commit()

# function to get movie id, title, keywords, genres, actors and director
def get_relevant_movie_fields(session):
    genre_subq = (
        select(
            Movie.id,
            func.group_concat(Genre.genre_name, ' ').label('genres')
        ) 
        .join(Movie.genres)
        .group_by(Movie.id)
        .subquery()
    )
    keyword_subq = (
        select(
            Keyword.movie_id,
            Keyword.keywords
        )
        .subquery()
    )
    actor_subq = (
        select(
            Actor.movie_id,
            func.group_concat(Actor.actor_name, ',').label('actors')
        )
        .group_by(Actor.movie_id)
        .subquery()
    )

    query = (
        select(
            Movie.id,
            Movie.title,
            keyword_subq.c.keywords,
            genre_subq.c.genres,
            actor_subq.c.actors,
            Movie.director,
            Movie.year,
            Movie.popularity
        )
        .join(genre_subq, Movie.id == genre_subq.c.id, isouter=True)
        .join(keyword_subq, Movie.id == keyword_subq.c.movie_id, isouter=True)
        .join(actor_subq, Movie.id == actor_subq.c.movie_id, isouter=True)
    )    

    return session.execute(query)


def get_movies_as_documents():
    engine = create_engine(DB_LOCATION)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    # session = Session()
    with Session() as session:
        # movies_with_title_genres_tags = get_movies_with_title_genres_tags(session)
        relevant_movie_fields = get_relevant_movie_fields(session)
        # Format results into structure required to be added to Marqo index
        # Combine title, genres and tags into a single field to be indexed
        # Example: [{"id": "1", "title_genres_tags": "Toy Story Animation Children's", "title": "Toy Story", "genres": ["Animation", "Children's"], "tags": []}]
        return format_movies(relevant_movie_fields)

def format_movies(results)-> List[Dict[str, Any]]:
    """Format database results into movie documents for search indexing.
    
    Combines movie title, genres, and tags into a single searchable field
    while preserving individual fields for filtering and display.
    
    Args:
        results: SQLAlchemy result set containing movie records with:
            - id: Movie identifier
            - title: Movie title
            - genres: Space-separated genre names
            - tags: Space-separated user tags
    
    Returns:
        List[Dict[str, Any]]: List of formatted movie documents:
            {
                "id": "123",
                "title_genres_tags": "Movie Title Action Adventure sci-fi great",
                "title": "Movie Title",
                "genres": ["Action", "Adventure"],
                "tags": ["sci-fi", "great"]
            }
    
    Example:
        >>> results = session.execute(movie_query)
        >>> documents = format_movies(results)
        >>> print(documents[0])
        {
            "id": "1",
            "title_genres_tags": "Toy Story Animation Children",
            "title": "Toy Story",
            "genres": ["Animation", "Children"],
            "tags": []
        }
    """
    formatted_movies = []
    for movie in results:
        vector_field = movie.title.strip()
        keywords = []
        if (movie.keywords):
            keywords = movie.keywords.replace(","," ")
            vector_field+= " "+keywords
        genres = []
        if(movie.genres):
            genres = movie.genres.split(" ")
            vector_field+= " "+movie.genres
        if(movie.actors):
            actors = movie.actors.split(",")
            vector_field+= " "+movie.actors
        if(movie.director):
            director = movie.director
            vector_field+= " "+movie.director
        formatted_movie = {
            "id": str(movie.id),
            "text": vector_field,
            "title": movie.title,
            "genres": genres,
            "actors": actors,
            "director": director,
            "year":str(movie.year),
            "popularity":movie.popularity
        }
        # print(formatted_movie)
        formatted_movies.append(formatted_movie)
    return formatted_movies
    
def attach_imdb_links(recommendations):
    engine = create_engine(DB_LOCATION)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    with Session() as session:
        try:
            # Query links table
            links_query = session.query(Link).all()
            imdbID_dict = {link.movie_id: link.imdb_id for link in links_query}
            
            for movie in recommendations:
                movie_id = int(movie['id'])
                if movie_id in imdbID_dict:
                    imdbID = f"{imdbID_dict[movie_id]:07d}"
                    movie['imdb_id'] = imdbID
                    movie['imdb_url'] = 'https://www.imdb.com/title/tt' + imdbID

            return recommendations
        
        except Exception as e:
            print(f"Error adding IMDB links: {e}")
            return []

def attach_posters(recommendations):
    engine = create_engine(DB_LOCATION)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    with Session() as session:
        try:
            # Query links table
            links_query = session.query(Link).all()
            posterPath_dict = {link.movie_id: link.poster_path for link in links_query}
            
            for movie in recommendations:
                movie_id = int(movie['id'])
                if movie_id in posterPath_dict:
                    posterPath = posterPath_dict[movie_id]
                    movie['poster_url'] = "https://image.tmdb.org/t/p/w200"+posterPath
            return recommendations
        
        except Exception as e:
            print(f"Error adding posters: {e}")
            return []
        
def attach_ratings_overviews(recommendations):
    engine = create_engine(DB_LOCATION)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    with Session() as session:
        try:
            # Query Movie table
            movie_query = session.query(Movie).all()
            movie_dict = {movie.id: movie for movie in movie_query}

            for movie in recommendations:
                movie_id = int(movie['id'])
                if movie_id in movie_dict:
                    movie_details = movie_dict[movie_id]
                    movie['rating'] = movie_details.popularity
                    movie['plot'] = movie_details.overview
        
            return recommendations
        except Exception as e:
            print(f"Error adding ratings and overviews: {e}")
            return []