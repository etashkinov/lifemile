import postgresql
import json


def get():
    return SQLPersister(port=5432, database="postgres")


class SQLPersister:
    def __init__(self, user="postgres", password="postgres", host="localhost", port=5432, database="lifemile") -> None:
        self.db = postgresql.open('pq://{}:{}@{}:{}/{}'.format(user, password, host, port, database))

    def persist(self, photo):
        with self.db.xact():
            photo_stmt = self.db.prepare(
                "INSERT INTO photo(source_type, source_id, latitude, longitude, creation_time) VALUES ($1, $2, $3, $4, $5)")
            source_id = photo['source_id']
            photo_stmt(photo['type'], source_id, photo['geo'][0], photo['geo'][1], photo['time'])

            last_row = self.db.prepare("SELECT id FROM photo WHERE source_id=$1")(source_id)
            faces = photo['faces']
            for f in faces:
                photo_stmt = self.db.prepare("INSERT INTO face(photo_id, face_id, encoding)  VALUES ($1, $2, $3)")
                photo_id = last_row[0][0]
                face_id = '-'.join(map(str, f[0]))
                encoding = json.dumps(list(f[1]))
                print(encoding)
                photo_stmt(photo_id, face_id, encoding)

    def get_last_id(self):
        ids = self.db.prepare("SELECT source_id FROM photo ORDER BY id DESC LIMIT 1")()
        return ids[0][0] if len(ids) > 0 else None

    def exists(self, source_id):
        ids = self.db.prepare("SELECT source_id FROM photo WHERE source_id = $1")(source_id)
        return len(ids) > 0

    def get_faces(self):
        return self.db.prepare("SELECT id, encoding FROM face")()

    def get_unknown_faces(self):
        return self.db.prepare("SELECT id, encoding FROM face WHERE person_id is null ORDER BY id")()

    def update_face(self, id, person_id):
        return self.db.prepare("UPDATE face SET person_id = $1 WHERE id = $2")(person_id, id)

    def create_person(self, name):

        try:
            self.db.prepare("INSERT INTO person(name) VALUES ($1)")(name)
        except postgresql.exceptions.UniqueError:
            print(name, "already exists")

        return self.db.prepare("SELECT id FROM person WHERE name=$1")(name)[0][0]

    def get_person_faces(self, person_id):
        return self.db.prepare(
            "SELECT p.source_id, p.source_type, f.face_id"
            " FROM face f "
            " JOIN photo p ON p.id = f.photo_id "
            " WHERE f.person_id = $1")(
            person_id)

    def get_persons(self):
        return self.db.prepare(
            "SELECT person_id, encoding"
            " FROM face "
            " WHERE person_id is not null")()

    def get_person(self, person_id):
        return self.db.prepare(
            "SELECT name"
            " FROM person "
            " WHERE id = $1")(person_id)[0]['name']

    def get_person_ids(self):
        return self.db.prepare(
            "SELECT id"
            " FROM person "
            " ORDER BY id")

    def get_persons_by_days(self):
        return self.db.prepare(
            "select day, person_id, count(id) as cnt from "
            "("
            "   SELECT date_trunc('day', creation_time) as day, f.id, f.person_id "
            "   FROM photo p "
            "   join face f on f.photo_id = p.id "
            ") as a "
            "WHERE person_id is not null "
            "group by day,person_id")
