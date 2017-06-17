import face_recognition
import numpy as np
import sys
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from PIL.ExifTags import TAGS, GPSTAGS
from file_source import FileSourceStream, FileSource
from sql_persister import SQLPersister
import json
from datetime import datetime


def extract_faces(image):
    image_array = np.array(image, dtype=np.uint8)
    face_locations = face_recognition.face_locations(image_array)
    encodings = face_recognition.face_encodings(image_array, known_face_locations=face_locations)

    return list(zip(face_locations, encodings))


def show_faces(image, faces):
    # Create figure and axes
    fig, ax = plt.subplots(1)

    # Display the image
    plt.imshow(image)

    for face in faces:
        location = face[0]
        # Create a Rectangle patch

        x = int(location[3])
        y = int(location[0])
        w = int(location[2]) - y
        h = int(location[1]) - x

        rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='r', facecolor='none')

        # Add the patch to the Axes
        ax.add_patch(rect)

    plt.show()


def show_image_faces(image):
    faces = extract_faces(image)
    show_faces(image, faces)


def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]

                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value

    return exif_data


def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None


def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


def get_lat_lon(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lon = None

    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]

        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat

            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon

    return lat, lon


def extract_data(source):
    image = source.get_image()
    faces = extract_faces(image)

    try:
        exif = get_exif_data(image)
        geo = get_lat_lon(exif)
        timestamp = get_image_date(exif, source)
    except Exception as e:
        print("No exif for", source.get_id(), e)
        geo = None, None
        timestamp = None

    return {"type": source.get_type(), "source_id": source.get_id(), "time": timestamp, "geo": geo, "faces": faces}


def get_image_date(exif, source):
    if 'DateTimeOriginal' in exif:
        timestamp = datetime.strptime(exif['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
    else:
        timestamp = source.get_modify_date()
    return timestamp


def dump(source_stream, persister):
    source = source_stream.next()
    while source:
        print("Extract from", source.get_id())
        if not persister.exists(source.get_id()):
            data = extract_data(source)
            print("Extracted data. Timestamp", data['time'], ", geo", data['geo'], ", faces", [f[0] for f in data['faces']])
            persister.persist(data)
        else:
            print(source.get_id(), "already exists")
        source = source_stream.next()


def dump_folder(folder):
    persister = SQLPersister(port=5432, database="postgres")
    stream = FileSourceStream(folder)
    dump(stream, persister)


def fit_faces():
    persister = SQLPersister(port=5432, database="postgres")
    faces = persister.get_faces()

    persons = {}
    for face in faces:
        print("Face", face[0])
        match = None
        enc_array = np.array(json.loads(face[1]))
        for person in persons:
            print("Person", person)
            result = face_recognition.compare_faces(persons[person], enc_array)
            print("Comparison", result)
            vote = 0
            for r in result:
                if r:
                    vote += 1
            print("Vote", vote)

            if vote > 0 and (not match or match[1] < vote):
                match = person, vote
                print("New match", match)

        if not match:
            name = "Person " + str(len(persons))
            person = persister.create_person(name)
            persons[person] = [enc_array]
            print("New person found", name, person)
        else:
            person = match[0]
            persons[person].append(enc_array)
            print("Person detected", person)

        persister.update_face(face[0], person)
        print("Face", face[0], "assigned to person", person)


dump_folder(sys.argv[1])
# fit_faces()
# data = extract_data(FileSource(r"E:\Старые фотографии\2007_04_26\IMG_0919.JPG"))
# print(data)
