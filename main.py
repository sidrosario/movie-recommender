from dataclasses import dataclass
import json
import logging
from openai import OpenAI
import os
from pydantic import Field, ValidationError, BaseModel
from typing import List, Literal, Optional, Tuple

from config import GENRES, NUM_SEARCH_RESULTS, USER_REQUESTS
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

def construct_user_query(preferences: UserPreferences) -> tuple[str, str]:
        positive_terms = []
        filters = []

        if preferences.title:
            positive_terms.append(preferences.title)

        # Add keywords
        if (preferences.keywords):
            positive_terms.extend(preferences.keywords)

        # Add positive genres
        if(preferences.genres):
            positive_terms.extend(genre[0] for genre in preferences.genres if genre[1] == 1)
            filters.extend(f"genres IN ({genre[0]})" for genre in preferences.genres if genre[1] == 1)
        
        # Add positive actors
        if(preferences.actors): 
            positive_terms.extend(actor[0] for actor in preferences.actors if actor[1] == 1)
            filters.extend(f"actors:({actor[0]})" for actor in preferences.actors if actor[1] == 1)
        
        # Build negative filters
        negative_genres = []
        if(preferences.genres):
            negative_genres = [genre[0] for genre in preferences.genres if genre[1] == 0]
        if negative_genres:
            filters.extend([f"NOT genres IN ({genre})" for genre in negative_genres])

        query = " ".join(positive_terms)
        filters = " AND ".join(filters)
        
        return query, filters

def print_results(results):
    # Print results with error handling
    for result in results.get('hits', []):
        try:
            print(f"Movie: {result.get('title', 'No title')}, Score: {result.get('_score', 'No score')}")
        except KeyError as e:
            logger.error(f"Missing key in result: {e}")
            print(f"Raw result: {result}")

def get_top_results(results, limit = NUM_SEARCH_RESULTS) -> None:
    """Print top 'limit' results sorted by score"""
    # Get hits and sort by score
    hits = results.get('hits', [])
    # update the score of a movie to 0.3*score + 0.7*popularity
    
    # map(lambda x: x.update({' score': x.get('_score',0)*0.3 + (movie_ratings[x.get('id',0)]/5.0)*0.7}),hits)
    # map(hits, lambda x: x.update({'_score': x.get('_score',0)*0.3+})
    print("LENGTH OF HITS:",len(hits))
    sorted_hits = sorted(hits, 
                        key=lambda x: float(x.get('popularity', 0)), 
                        reverse=True)
    
    # Take top N results
    return sorted_hits[:limit]
        
def print_results(top_hits):
        # Print formatted results
    try:
        print("\nTop {} Recommendations:".format(len(top_hits)))
        print("-" * 50)
        for i, movie in enumerate(top_hits, 1):
            print(f"{i}. Movie: {movie.get('title', 'No title')}")
            print(f"   Score: {movie.get('_score', 'No score'):.3f}")
            # print(f"   Genres: {movie.get('genres', 'None')}")
            # print(f"   Tags: {movie.get('tags', 'None')}\n")
            
    except Exception as e:
        logger.error(f"Error printing results: {e}")

def main():
    try:
        # Change the index for different user requests.
        input_sentence = USER_REQUESTS[1]        
        top_hits = find_recommendations(input_sentence)
        print_results(top_hits)
        
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise

def find_recommendations(input_sentence: str) -> List[str]:
    try:
        # Extract tags using OpenAI API
        output = extract_tags_from_input(input_sentence)
        logger.info(output) # Output from OpenAI
        print(output)
        preferences = UserPreferences.from_json(json.loads(output))

        keywords, filter = construct_user_query(preferences)

        # Search with debug info
        results = search_movies(keywords,filter)
        top_hits = get_top_results(results)
        print_results(top_hits)
        return top_hits
        
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main()