from PIL import Image
from matplotlib import pyplot as plt

import source_manager
from sql_persister import SQLPersister


def show_person_faces(persister, person_id):
    faces = persister.get_person_faces(person_id)

    for face in faces:
        photo_source_id = face[0]
        photo_source_type = face[1]
        face_location = face[2].split("-")

        image = source_manager.get(photo_source_id, photo_source_type).get_image()

        x1 = int(face_location[3])
        y1 = int(face_location[0])
        x2 = int(face_location[2])
        y2 = int(face_location[1])

   #     crop_image = image.crop((x1, y1, x2, y2))

        plt.imshow(image)
        plt.show()


persister = SQLPersister(port=5432, database="postgres")
show_person_faces(persister, 1792)
