import json
import numpy as np
import face_recognition

import sql_persister

__CONFIDENCE_THRESHOLD__ = 0.8


def fit_faces():
    persister = sql_persister.get()
    faces = persister.get_unknown_faces()

    persons = get_persons(persister)

    for face in faces:
        try:
            fit_face(face, persister, persons)
        except Exception as e:
            print("Failed to assign face", face[0], "to person:", e)


def fit_face(face, persister, persons):
    face_encoding = np.array(json.loads(face[1]))
    matched_person, confidence = match_face(face_encoding, persons)
    if not matched_person:
        matched_person = add_new_person(persons)

    persons[matched_person].append(face_encoding)
    persister.update_face(face[0], matched_person)
    print("Face", face[0], "assigned to person", persister.get_person(matched_person), "with confidence", confidence)


def add_new_person(persons):
    name = "Person " + str(len(persons))
    person = sql_persister.get().create_person(name)
    persons[person] = []
    return person


def match_face(face_encoding, persons):
    match = None, None
    for person in persons:
        result = face_recognition.compare_faces(persons[person], face_encoding)
        vote = np.mean([1 if r else 0 for r in result])
        if vote > __CONFIDENCE_THRESHOLD__ and (not match[1] or match[1] < vote):
            match = person, vote

    return match


def get_persons(persister):
    raw_persons = persister.get_persons()
    persons = {}
    for person in raw_persons:
        person_id = person['person_id']
        encoding_ = np.array(json.loads(person['encoding']))
        if person_id in persons:
            persons[person_id].append(encoding_)
        else:
            persons[person_id] = [encoding_]
    return persons


fit_faces()
