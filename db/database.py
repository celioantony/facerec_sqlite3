import os
import sqlite3
from sqlite3 import Error
from .tables import person_table, faces_table

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def load_database_in_memory(conn_source, conn_memory):
    conn_source.backup(conn_memory)
    print('Database loaded in memory.')
    

def migrate(conn=None):
    
    if conn is not None:
        # create person table
        create_table(conn, person_table)
        # create faces table
        create_table(conn, faces_table)
        
        print('Migration database created successfully.')
        
    else:
        print('Error! cannot create the database connection.')