import json
import logging
from openai import OpenAI
import os
from pydantic import ValidationError, BaseModel
from typing import List, Optional

from vectordb import search_movies

 # Setup logging
logging.basicConfig(filename='runs.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieTags(BaseModel):
    genre: str
    actor: str
    keywords: List[str]

def get_user_input() -> str:
    return "A sci-fi movie that explores futuristic technology, space travel, and the complexities of human emotions."
    #return "an epic historical drama filled with battles, political intrigue, and a strong female lead"
    #return "a heartwarming romantic comedy set in a picturesque small town with witty dialogue and charming characters."
    #return "A horror movie with psychological depth, eerie settings, and a suspenseful build-up starring Mel Gibson."
    
def extract_tags_from_input(input_sentence: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f'''Extract genre, actor, keywords from the following sentence: {input_sentence}.
        Return the extracted tags as a JSON object as below:
         -'genre': genre of the movie,
         -'actor': actor,
         -'keywords': keywords

         Return only a valid JSON object with the extracted tags. Do not include formatting characters like triple backquotes.
         
         {{
    '''
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return '{'+response.choices[0].message.content

def validate_tags(json_string: str) -> Optional[MovieTags]:
    try:
        json_data = json.loads(json_string)
        validated_data = MovieTags(**json_data)
        #print("Valid JSON:", validated_data.model_dump())
        return validated_data
    except ValidationError as e:
        print(f"Error validating JSON: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

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
            print(f"   Metadata: {movie.get('metadata', 'No metadata')}\n")
            
    except Exception as e:
        logger.error(f"Error printing results: {e}")

def main():
    
    # Get user input
    input_sentence = get_user_input()
    
    # Extract tags using OpenAI
    output = extract_tags_from_input(input_sentence)
    
    try:
        output_json = json.loads(output)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return
    
    # Validate tags
    tags = validate_tags(output)
    if not tags:
        return
    
    user_keywords = f"{output_json['genre']} {output_json['actor']} {' '.join(output_json['keywords'])}"
    
    #user_keywords = "inspirational friendship Al Pacino"
    
    try:
        # Search with debug info
        results = search_movies(user_keywords)
        print_top_results(results)
        
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main()