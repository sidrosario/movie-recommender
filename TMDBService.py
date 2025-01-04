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
                return int(row['tmdbId'].iloc[0])
            return None
        except Exception as e:
            print(f"Error converting IMDB ID {imdb_id}: {e}")
            return None

    def get_movie_poster_rating_overview(self, tmdb_id: int) -> Optional[dict]:
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
        
    # def get_movie_overview(self, tmdb_id: int) -> Optional[str]:
    #     try:
    #         movie = self.movie.details(tmdb_id)
    #         if movie:
    #             return movie.overview if movie.overview else None
    #         return None
    #     except Exception as e:
    #         print(f"Error fetching overview for TMDB ID {tmdb_id}: {e}")
    #         return None
    
    # def get_movie_actors(self, tmdb_id: int) -> Optional[list]:
    #     try:
    #         credits = self.movie.credits(tmdb_id)
    #         if credits:
    #             return [actor['name'] for actor in credits['cast'][:5]]
    #         return None
    #     except Exception as e:
    #         print(f"Error fetching actors for TMDB ID {tmdb_id}: {e}")
    #         return None
    
    # def get_movie_director(self, tmdb_id: int) -> Optional[str]:
    #     try:
    #         credits = self.movie.credits(tmdb_id)
    #         if credits:
    #             for crew in credits['crew']:
    #                 if crew['job'] == 'Director':
    #                     return crew['name']
    #         return None
    #     except Exception as e:
    #         print(f"Error fetching director for TMDB ID {tmdb_id}: {e}")
    #         return None
    
    def get_overview_actors_director(self, tmdb_id):
        actors, director, overview = None, None, None
        try:
            movie = self.movie.details(tmdb_id)
            credits = self.movie.credits(tmdb_id)
            
            if movie:
                overview = movie.overview if movie.overview else None
            
            if credits:
                actors = []
                for actor in credits['cast']:
                    actors.append(actor['name'])
                    if (len(actors) == 5):
                        break
                    
                # actors = [actor['name'] for actor in credits['cast'][:5]]
                for crew in credits['crew']:
                    if crew['job'] == 'Director':
                        director = crew['name']
                        break
                
        except Exception as e:
            print(f"Error fetching details for TMDB ID {tmdb_id}: {e}")

        return overview, actors, director
    
    def get_movie_keywords(self,tmdb_id: int) -> Optional[list]:
        try:
            keywords = self.movie.keywords(tmdb_id)
            if keywords:
                return [keyword['name'] for keyword in keywords['keywords']]
            return None
        except Exception as e:
            print(f"Error fetching keywords for TMDB ID {tmdb_id}: {e}")
            return None