#Initialiser for the app. Initialise the SQLite DB and also the Marqo DB.
from database import init_db
from vectordb import init_marqo_db

init_db()
init_marqo_db()