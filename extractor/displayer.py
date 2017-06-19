import matplotlib.gridspec as gridspec
from matplotlib import pyplot as plt

import source_manager
import sql_persister


def show_person_faces(persister, person_id):

    faces = persister.get_person_faces(person_id)

    num_images = min((16, len(faces)))
    rows = 4
    cols = max(int(num_images / rows),1)
    num_images = cols * rows

    plt.title('Person with id ' + str(person_id))
    gs = gridspec.GridSpec(cols, rows)

    ax = [plt.subplot(gs[i]) for i in range(num_images)]

    for i, face in enumerate(faces[:num_images]):
        photo_source_id = face[0]
        photo_source_type = face[1]

        image = source_manager.get(photo_source_id, photo_source_type).get_image()

        location = get_location(face[2])

        x1, x2, y1, y2 = expand_location(location, 0.1)

        crop_image = image.crop((x1, y1, x2, y2))
        # Display the image
        ax[i].imshow(crop_image)
        ax[i].axis('off')

    plt.show()


def expand_location(l, extend_ratio):
    x1 = int(l[0] - (l[1] - l[0]) * extend_ratio)
    x2 = int(l[1] + (l[1] - l[0]) * extend_ratio)
    y1 = int(l[2] - (l[3] - l[2]) * extend_ratio)
    y2 = int(l[3] + (l[3] - l[2]) * extend_ratio)
    return x1, x2, y1, y2


def get_location(face_id):
    l = face_id.split("-")
    y1 = int(l[0])
    x2 = int(l[1])
    y2 = int(l[2])
    x1 = int(l[3])
    return x1, x2, y1, y2


persister = sql_persister.get()

ids = persister.get_person_ids()
for id in list(ids):
    show_person_faces(persister, id['id'])
