import queue
import numpy as np
import face_recognition
from threading import Thread
from multiprocessing import current_process
from settings import known_faces_person_ids, \
    known_faces_encodings, \
    known_person


def face_ident(unknown_face):

    person_ids = []
    person_face_framepos = []
    identified_people = []

    face_locations = face_recognition.face_locations(unknown_face)
    unknown_face_encodings = face_recognition.face_encodings(
        unknown_face, face_locations)
    
    if len(unknown_face_encodings) > 0 and len(known_faces_encodings) > 0:

        for (top, right, bottom, left), unknown_face_enc in zip(face_locations, unknown_face_encodings):
            matches = face_recognition.compare_faces(
                known_faces_encodings, unknown_face_enc)
            face_distances = face_recognition.face_distance(
                known_faces_encodings, unknown_face_enc)
            best_match_index = np.argmin(face_distances)


            if matches[best_match_index] and \
                    (known_faces_person_ids[best_match_index] in known_faces_person_ids):
                person_id = known_faces_person_ids[best_match_index]

                person_ids.append(person_id)
                person_face_framepos.append((top, right, bottom, left))
            
            else:
                identified_people = [{'fullname': 'Desconhecido', 'registration': '', 'frame_pos': (
                    top, right, bottom, left)}]

    if len(person_ids) > 0 and len(person_face_framepos) > 0:

        for person_id, frame_pos in zip(person_ids, person_face_framepos):
            people = known_person[person_id]
            people['frame_pos'] = frame_pos
            identified_people.append(people)

    return identified_people

    # return [{'fullname': 'Desconhecido', 'registration': 0, 'position': (0, 0, 0, 0)}]


class RecognitionWorker(Thread):

    def __init__(self, queue_recog, queue_stream, name):
        Thread.__init__(self)
        self.queue_recog = queue_recog
        self.queue_stream = queue_stream
        self.name = name

    def run(self):
        while True:
            if not self.queue_recog.empty():
                frame = self.queue_recog.get()
                rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])
                
                try:
                    ident = face_ident(rgb_frame)
                    self.queue_stream.put(ident)
                finally:
                    self.queue_recog.task_done()
                    
                    
def multiprocessor_recog(queue_recog):
    while True:
        try:
            frame = queue_recog.get()
            print(' - task - ', current_process().name)
        except queue.Empty:
            break
        else:
            print(' - task done - ')
    
    return True