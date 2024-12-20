from datetime import datetime, timezone
import pandas as pd
from sqlalchemy import create_engine, select,func
from sqlalchemy.orm import sessionmaker
from config import CSV_FILES
from models import Base, Movie, Genre, Rating, Tag


def init_db():
    engine = create_engine('sqlite:///movies.db')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    with Session() as session:
        try:
            load_movies_from_csv(session, CSV_FILES['movies'])
            load_ratings_from_csv(session, CSV_FILES['ratings'])
            load_tags_from_csv(session, CSV_FILES['tags'])
            print("Data loading completed successfully")
        except Exception as e:
            print(f"Error loading data: {e}")
        session.close()
    
    engine.dispose()


def load_movies_from_csv(session, csv_path):
    df = pd.read_csv(csv_path)
    
    # Create genres first
    all_genres = set()
    for genres_str in df['genres']:
        all_genres.update(genres_str.split('|'))
    
    genre_dict = {}
    for genre_name in all_genres:
        genre = Genre(genre_name=genre_name)
        session.add(genre)
        genre_dict[genre_name] = genre
    
    # Create movies with their genres
    for _, row in df.iterrows():
        title_with_year = row['title']
        # Extract year from title
        year = None
        if '(' in title_with_year:
            # print(title_with_year)
            title = title_with_year.rsplit('(', 1)[0].strip()
            year = int(title_with_year.rsplit('(', 1)[1].strip().rstrip(')'))
        else:
            title = title_with_year
            
        movie = Movie(
            id=row['movieId'],
            title=title,
            year=year
        )
        
        # Add genres
        for genre_name in row['genres'].split('|'):
            movie.genres.append(genre_dict[genre_name])
        
        session.add(movie)
    
    session.commit()

def convert_unix_timestamp(timestamp):
    try:
        # Convert Unix timestamp to UTC datetime object
        return datetime.fromtimestamp(float(timestamp), tz=timezone.utc)
    except (ValueError, TypeError) as e:
        print(f"Error converting timestamp {timestamp}: {e}")
        return None

def load_ratings_from_csv(session, csv_path):
    df = pd.read_csv(csv_path)
    
    for _, row in df.iterrows():
        rating = Rating(
            user_id=row['userId'],
            movie_id=row['movieId'],
            rating=row['rating'],
            timestamp=convert_unix_timestamp(row['timestamp'])
        )
        session.add(rating)

    session.commit()

def load_tags_from_csv(session, csv_path):
    df = pd.read_csv(csv_path)
    
    for _, row in df.iterrows():
        tag = Tag(
            user_id=row['userId'],
            movie_id=row['movieId'],
            tag=row['tag'],
            timestamp=convert_unix_timestamp(row['timestamp'])
        )
        session.add(tag)

    session.commit()

def get_movies_with_metadata():
    """Get movies with combined genres and tags as metadata"""
    engine = create_engine('sqlite:///movies.db')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Subquery to get genres as string
        genre_subq = (
            select(
                Movie.id,
                func.group_concat(Genre.genre_name, ' ').label('genres')
            )
            .join(Movie.genres)
            .group_by(Movie.id)
            .subquery()
        )


        # Subquery to get tags as string
        tag_subq = (
            select(
                Movie.id,
                func.group_concat(Tag.tag, ' ').label('tags')
            )
            .join(Tag)
            .group_by(Movie.id)
            .subquery()
        )

        # Main query combining movies with genres and tags
        query = (
            select(
                Movie.id,
                Movie.title,
                genre_subq.c.genres,
                tag_subq.c.tags
            )
            .join(genre_subq, Movie.id == genre_subq.c.id, isouter=True)
            .join(tag_subq, Movie.id == tag_subq.c.id, isouter=True)
        )

        results = session.execute(query).all()
        
        # Format results into required structure
        formatted_movies = []
        for movie in results:
            metadata = f"{movie.genres or ''} {movie.tags or ''}".strip()
            formatted_movies.append({
                "id": str(movie.id),
                "title": movie.title,
                "metadata": metadata
            })
        
        session.close()
        engine.dispose()

        return formatted_movies

    except Exception as e:
        #logger.error(f"Error getting movies with metadata: {e}")
        return []


if __name__ == '__main__':
    init_db()