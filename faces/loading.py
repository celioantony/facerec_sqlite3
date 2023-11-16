from .utils import decode_nparray
from db.operations import query_sql
import numpy as np

def load_training_in_memory(conn):

    known_faces_person_ids = []
    known_faces_encodings = []

    query_faces_sql = """
        SELECT * FROM faces
    """

    rows_faces = query_sql(conn, query_faces_sql)
    for id, face_encodeing_bytes, person_id in rows_faces:
        face_encoding = decode_nparray(face_encodeing_bytes)
        known_faces_person_ids.append(person_id)
        known_faces_encodings.append(face_encoding)
        
    known_faces_person_ids = np.asarray(known_faces_person_ids)
    known_faces_encodings = np.asarray(known_faces_encodings)

    query_person_sql = """
        SELECT * FROM person
    """

    rows_person = query_sql(conn, query_person_sql)
    known_person = dict((id, ({'fullname': str.title(' '.join(
        [first_name, last_name])), 'registration': registration})) \
                for id, first_name, last_name, registration in rows_person)
    
    # print('known_faces_person_ids: ', len(known_faces_person_ids))
    # print('known_faces_encodings: ', len(known_faces_encodings))
    # print(known_person)

    return (known_faces_person_ids, known_faces_encodings, known_person)