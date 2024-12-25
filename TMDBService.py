import pandas as pd
from tmdbv3api import TMDb, Movie
import os
from typing import Optional

from config import CSV_FILES

class TMDBService:
    def __init__(self):
        self.tmdb = TMDb()
        self.tmdb.api_key = os.getenv('TMDB_API_KEY')
        print('TMDB KEY: ', self.tmdb.api_key)
        self.movie = Movie()
        self.base_image_url = "https://image.tmdb.org/t/p/w200"
        self.links_df = pd.read_csv(CSV_FILES['links'])

    def get_tmdb_id(self, imdb_id: str) -> Optional[int]:
        try:
            imdb_id = int(imdb_id.replace('tt', ''))
            row = self.links_df[self.links_df['imdbId'] == imdb_id]
            if not row.empty:
                return row['tmdbId'].iloc[0]
            return None
        except Exception as e:
            print(f"Error converting IMDB ID {imdb_id}: {e}")
            return None

    def get_movie_details(self, tmdb_id: int) -> Optional[dict]:
        try:
            movie = self.movie.details(tmdb_id)
            if movie:
                return {
                    "poster_url": f"{self.base_image_url}{movie.poster_path}" if movie.poster_path else None,
                    "rating": movie.vote_average if movie.vote_average else None,
                    "plot": movie.overview if movie.overview else None
                }
            return None
        except Exception as e:
            print(f"Error fetching details for TMDB ID {tmdb_id}: {e}")
            return None