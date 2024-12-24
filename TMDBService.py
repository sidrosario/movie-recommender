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
            # Remove 'tt' prefix if present
            imdb_id = imdb_id.replace('tt', '')
            # Convert to integer
            imdb_id = int(imdb_id)
            # Look up TMDB ID
            row = self.links_df[self.links_df['imdbId'] == imdb_id]
            if not row.empty:
                return row['tmdbId'].iloc[0]
            return None
        except Exception as e:
            print(f"Error converting IMDB ID {imdb_id}: {e}")
            return None
    
    def get_poster_url(self, tmdb_id: int) -> Optional[str]:
        try:
            movie = self.movie.details(tmdb_id)
            if movie.poster_path:
                return f"{self.base_image_url}{movie.poster_path}"
            return None
        except Exception as e:
            print(f"Error fetching poster for TMDB ID {tmdb_id}: {e}")
            return None