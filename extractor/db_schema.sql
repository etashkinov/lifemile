CREATE TABLE photo
    (
   id SERIAL not null CONSTRAINT photo_pk PRIMARY KEY,
   source_type varchar not null,
   source_id varchar  not null unique,
   latitude double precision,
   longitude double precision,
   creation_time timestamp
    );


CREATE TABLE person
    (
   id SERIAL not null CONSTRAINT person_pk PRIMARY KEY,
   name varchar not null unique
    );

CREATE TABLE face
    (
   id SERIAL not null CONSTRAINT face_pk PRIMARY KEY,
   photo_id INTEGER REFERENCES photo (id),
   person_id INTEGER REFERENCES person (id),
   face_id varchar  not null,
   encoding jsonb
    );