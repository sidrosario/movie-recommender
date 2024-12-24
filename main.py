from dataclasses import dataclass
import json
import logging
from openai import OpenAI
import os
from pydantic import Field, ValidationError, BaseModel
from typing import List, Literal, Optional, Tuple

from config import GENRES, USER_REQUESTS
from vectordb import search_movies

 # Setup logging
logging.basicConfig(filename='runs.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserPreferences:
    title: Optional[str]
    genres: List[Tuple[str, int]]
    actors: List[Tuple[str, int]]
    era: Optional[str]
    keywords: List[str]

    @classmethod
    def from_json(cls, data: dict) -> 'UserPreferences':
        return cls(
            title=data.get('title'),
            genres=data.get('genres', []),
            actors=data.get('actors', []),
            era=data.get('era'),
            keywords=data.get('keywords', [])
        )
    
# StrIntTuple = Tuple[str, Literal[0, 1]]
# class MovieTags(BaseModel):
#     title: Optional[str] = None
#     actors: Optional[List[StrIntTuple]] = Field(
#         default=None,
#         description="List of (actor, intent) tuples where intent is 0 (actor present in movie) or 1 (actor not present in movie)"
#     )
#     genres: Optional[List[StrIntTuple]] = Field(
#         default=None,
#         description="List of (genre, intent) tuples where intent is 0 (movie not of this genre) or 1 (movie of this genre)"
#     )
#     era: Optional[str] = None
#     keywords: Optional[List[str]] = None

def extract_tags_from_input(input_sentence: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # prompt1 = "Extract the tags. Do not infer any information. Include title only if it is a valid movie name."
    prompt = f'''Act as a specialized assistant who extracts tags from user input. The user will input a sentence describing the kind of movie they would like to watch. Extract the following tags from the input:
1. Movie Title: Also decide if the user wants to watch something similar to this movie or not.
2. Actors: Extract a list of actors if mentioned. For each actor specify whether the user would like that actor to be in the movie or not.
3. Genres: Extract a list of genres if mentioned. Each genre should be one of the following values: 
      ```{GENRES}```
For each genre specify whether the user would like to watch a movie of that genre or not. 
4. Era: If mentioned, include the era of the desired movie. Output one of two values, 'recent' or 'old'.
5. Keywords: Any other relevant keywords mentioned by the user.

Output the extracted tags in the JSON format as shown in the examples below. 
Examples:
1. User input: "I want to watch a action movie, but not a comedy, starring Tom Cruise. The movie should have good dialogues and a twist in the ending. I do not want to watch a Penelope Cruz movie."
   Output: {{
                     "title": null
                     "genres": [["action", 1], ["comedy", 0]]
                     "actors": [["Tom Cruise", 1], ["Penelope Cruz", 0]] 
                     "era": null
                     "keywords": ["good dialogues", "twist in the ending"]
                     }}

2. User input: "I want to watch an old dramatic musical. The movie should have great music and should be inspiring. "
   Output: {{
                     "title": null
                     "genres": [["musical", 1], ["drama", 1]]
                     "actors": null 
                     "era": "old"
                     "keywords": ["great music", "inspiring"]
                     }}

Do not infer any information. Include a title only if it is a valid movie name.
'''
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_sentence},
        ],
    )
        # response_format=MovieTags,
    result = completion.choices[0].message.content
    return result


# def validate_tags(json_string: str) -> Optional[MovieTags]:
#     try:
#         json_data = json.loads(json_string)
#         # validated_data = MovieTags(**json_data)
#         #print("Valid JSON:", validated_data.model_dump())
#         return validated_data
#     except ValidationError as e:
#         print(f"Error validating JSON: {e}")
#         return None
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON: {e}")
#         return None

def build_query(preferences: UserPreferences) -> tuple[str, str]:
        positive_terms = []
        negative_filters = []

        # Add positive genres
        if(preferences.genres):
            positive_terms.extend(genre[0] for genre in preferences.genres if genre[1] == 1)
        
        # Add positive actors
        if(preferences.actors): 
            positive_terms.extend(actor[0] for actor in preferences.actors if actor[1] == 1)
        
        # Add keywords
        positive_terms.extend(preferences.keywords)
        
        # Build negative filters
        negative_genres = []
        if(preferences.genres):
            negative_genres = [genre[0] for genre in preferences.genres if genre[1] == 0]
        if negative_genres:
            negative_filters = [f"NOT genres IN ({genre})" for genre in negative_genres]

        query = " ".join(positive_terms)
        filters = " AND ".join(negative_filters)
        
        return query, filters

def print_results(results):
    # Print results with error handling
    for result in results.get('hits', []):
        try:
            print(f"Movie: {result.get('title', 'No title')}, Score: {result.get('_score', 'No score')}")
        except KeyError as e:
            logger.error(f"Missing key in result: {e}")
            print(f"Raw result: {result}")

def print_top_results(results, limit: int = 10) -> None:
    """Print top 'limit' results sorted by score"""
    try:
        # Get hits and sort by score
        hits = results.get('hits', [])
        sorted_hits = sorted(hits, 
                           key=lambda x: float(x.get('_score', 0)), 
                           reverse=True)
        
        # Take top N results
        top_hits = sorted_hits[:limit]
        
        # Print formatted results
        print("\nTop {} Recommendations:".format(limit))
        print("-" * 50)
        for i, movie in enumerate(top_hits, 1):
            print(f"{i}. Movie: {movie.get('title', 'No title')}")
            print(f"   Score: {movie.get('_score', 'No score'):.3f}")
            print(f"   Genres: {movie.get('genres', 'None')}")
            print(f"   Tags: {movie.get('tags', 'None')}\n")
            
    except Exception as e:
        logger.error(f"Error printing results: {e}")

def main():
    try:
        # Change the index for different user requests.
        input_sentence = USER_REQUESTS[1]
        
        # Extract tags using OpenAI API
        output = extract_tags_from_input(input_sentence)
        print(output) # Output from OpenAI
        preferences = UserPreferences.from_json(json.loads(output))

        keywords, filter = build_query(preferences)

        # Search with debug info
        results = search_movies(keywords,filter)
        print_top_results(results)
        
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main()