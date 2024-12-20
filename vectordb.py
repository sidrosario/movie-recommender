import math
import marqo
from tqdm import tqdm
from database import get_movies_with_metadata

mq = marqo.Client(url="http://localhost:8882")
index_name = "mymovies"
        
def init_marqo_db():    
    try:
        movies = get_movies_with_metadata()
    
        # Initialize client
       
        # Check if index exists
        #logger.info(f"Creating index: {index_name}")
        if index_name in mq.get_indexes():
            print('Index already exists')
            mq.delete_index(index_name)
        print("Marqo indices: " , mq.get_indexes())
        # Comment out the following line to avoid re-creating the index
        mq.create_index(index_name)
        add_movies_to_index(movies)
    
    except Exception as e:
        print(f"Error initializing Marqo DB: {str(e)}")
        return None


def add_movies_to_index(movies):
    # Verify movies data
    #logger.info(f"Adding {len(movies)} documents to index")
    batch_size = 100
    
    # Add documents with progress
    total_docs = len(movies)
    num_batches = math.ceil(total_docs / batch_size)
    
    for i in tqdm(range(0, total_docs, batch_size), total=num_batches, desc="Indexing documents"):
        batch = movies[i:i + batch_size]
        try:
            mq.index(index_name).add_documents(
                documents=batch,
                tensor_fields=["metadata", "title"],
                client_batch_size=batch_size
            )
        except Exception as e:
            print(f"Error processing batch {i//batch_size + 1}: {str(e)}")
            continue

    #logger.info('Documents added successfully')
    
def search_movies(user_keywords):
    #logger.info(f"Searching for: {user_keywords}")
    results = mq.index(index_name).search(user_keywords)
    
    # Debug results structure
    #logger.info(f"Found {len(results['hits'])} results")
    return results
    
        