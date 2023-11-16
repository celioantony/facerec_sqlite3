from pathlib import Path
from db.database import create_connection
from faces.loading import load_training_in_memory

# Directory root of the project
BASE_DIR = Path(__file__).resolve().parent

# Database path
database = BASE_DIR / 'db' / 'facerec.db'

# Database connection disk
connection = create_connection(database)

# Load training in memory
known_faces_person_ids, \
known_faces_encodings, \
known_person = load_training_in_memory(connection)
