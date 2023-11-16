import os
import numpy as np
import face_recognition
from settings import BASE_DIR, connection
from db.operations import commit_sql
from settings import connection
from .utils import encode_nparray
import uuid

insert_person_sql = """
    INSERT INTO person (first_name, last_name, registration)
    VALUES (?, ?, ?)
"""

insert_face_sql = """
    INSERT INTO faces (facebytes, person_id)
    VALUES (?, ?)
"""


def get_faces(facename=None, fullpath=None):
    faces = []

    facesdir = None
    if facename and fullpath:
        facesdir = [(facename, fullpath)]
    else:
        facesdir = [(folder, BASE_DIR / 'datatraining' / folder)
                    for folder in os.listdir(BASE_DIR / 'datatraining')]

    def get_files(dirname):
        for file in os.listdir(dirname):
            if os.path.isfile(os.path.join(dirname, file)):
                yield file

    def is_not_none(path):
        return path != None

    for facename, facedir in facesdir:
        imgpaths = list(
            filter(is_not_none, [facedir / file for file in get_files(facedir)]))
        faces.append((facename, imgpaths))

    return faces


def training(faces=None):

    if not faces:
        faces = get_faces()

    for facename, facepaths in faces:
        firstname, lastname = facename.split('_')
        redistration = uuid.uuid4().hex[10:].upper()  # fake data
        person_data = (firstname, lastname, redistration)

        person_id = commit_sql(
            connection, insert_person_sql, person_data)

        for i, imgpath in enumerate(facepaths, start=1):
            image = face_recognition.load_image_file(imgpath)
            face_encoding = face_recognition.face_encodings(image)

            if len(face_encoding) > 0:
                face_encoding = face_encoding[0]

                encoded = encode_nparray(face_encoding)

                face_data = (encoded, person_id)

                commit_sql(connection, insert_face_sql, face_data)



