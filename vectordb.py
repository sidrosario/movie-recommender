import logging
import math
import marqo
from tqdm import tqdm
from database import get_movies_as_documents


settings = {
    "type": "structured",
    "allFields": [
        {"name": "id", "type": "text", "features": ["lexical_search"]},
        {"name": "title_genres_tags", "type": "text", "features": ["lexical_search"]},
        {"name": "title", "type": "text", "features": ["lexical_search"]},
        {"name": "genres", "type": "array<text>", "features": ["filter","lexical_search"]},
        {"name": "tags", "type": "array<text>", "features": ["filter","lexical_search"]},
    ],
    "tensorFields": ["title_genres_tags"],
}



mq = marqo.Client(url="http://localhost:8882")
index_name = "movies"
logger = logging.getLogger(__name__)
logger.handlers.clear()
logger.setLevel(logging.INFO)
#Add handler if none exists
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter) 
    logger.addHandler(handler)

def init_marqo_db():    
    try:
    
        # Initialize client
        indices = mq.get_indexes()
        for indexMap in indices['results']:
            print("Trying to delete index: ",indexMap['indexName'])
            mq.index(indexMap["indexName"]).delete()
        print("Marqo indices: " , mq.get_indexes())
        mq.create_index(index_name, settings_dict=settings)

        movies = get_movies_as_documents()
        add_movies_to_index(movies)
    
    except Exception as e:
        print(f"Error initializing Marqo DB: {str(e)}")
        return None


def add_movies_to_index(movies):
    # Verify movies data
    logger.info(f"Adding {len(movies)} documents to index")
    batch_size = 100
    
    # Add documents with progress
    total_docs = len(movies)
    num_batches = math.ceil(total_docs / batch_size)
    
    for i in tqdm(range(0, total_docs, batch_size), total=num_batches, desc="Indexing documents"):
        batch = movies[i:i + batch_size]
        try:
            result = mq.index(index_name).add_documents(
                documents=batch,
                client_batch_size=batch_size
            )
        except Exception as e:
            print(f"Error processing batch {i//batch_size + 1}: {str(e)}")
            continue

    logger.info('Documents added successfully')
    
def search_movies(user_keywords,filter):
    logger.info(f"Searching for q: {user_keywords}, filter: {filter}")
    if (filter):
        results = mq.index(index_name).search(
        q=user_keywords,
        filter_string=filter
        )
    else:
        results = mq.index(index_name).search(user_keywords)
    
    # Debug results structure
    #logger.info(f"Found {len(results['hits'])} results")
    return results
    
        