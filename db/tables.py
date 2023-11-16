# DECLARE TABLES

drop_tables = """
    DROP TABLE IF EXISTS person;
    DROP TABLE IF EXISTS faces;
"""

person_table = """
    CREATE TABLE IF NOT EXISTS person (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        registration INTEGER NOT NULL
    );
"""

faces_table = """
    CREATE TABLE IF NOT EXISTS faces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        facebytes TEXT NOT NULL,
        person_id INTEGER NOT NULL,
        FOREIGN KEY (person_id) REFERENCES person (id)
    );
"""