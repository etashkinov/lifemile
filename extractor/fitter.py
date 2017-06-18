import json
from collections import Counter

import numpy as np
import face_recognition

from sql_persister import SQLPersister


def fit_faces():
    persister = SQLPersister(port=5432, database="postgres")
    faces = persister.get_unknown_faces()

    persons = get_persons(persister)

    for face in faces:
        # print("Face", face[0])
        votes = []
        try:
            match = None
            enc_array = np.array(json.loads(face[1]))
            for person in persons:
                # print("Person", person)
                result = face_recognition.compare_faces(persons[person], enc_array)
                # print("Comparison", Counter(result))
                vote = 0.0
                for r in result:
                    if r:
                        vote += 1

                vote = vote/len(result)
                # print("Vote", vote)

                if vote > 0 and (not match or match[1] < vote):
                    match = person, vote
                #    print("New match", match)
                votes.append(vote)

            if not match or match[1] < 0.8:
                name = "Person " + str(len(persons))
                person = persister.create_person(name)
                persons[person] = [enc_array]
                # print("New person found", name, person)
            else:
                person = match[0]
                persons[person].append(enc_array)
                # print("Person detected", person)

            persister.update_face(face[0], person)
            print("Face", face[0], "assigned to person", persister.get_person(person), "with confidence", match[1] if match else None)
        except Exception as e:
            print("Failed to assign face to person:", e)


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