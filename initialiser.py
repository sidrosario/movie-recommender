#Initialiser for the app. Initialise the SQLite DB and also the Marqo DB.
from database import init_db,load_data
from vectordb import init_marqo_db

engine=init_db()
load_data(engine)
# init_marqo_db()