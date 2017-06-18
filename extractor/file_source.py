from PIL import Image
from os import walk, path
import os
from datetime import datetime


class FileSource:

    __TYPE = "file"

    def __init__(self, filename) -> None:
        self.filename = filename

    def get_id(self):
        return self.filename

    def get_image(self):
        return Image.open(self.filename)

    def get_modify_date(self):
        return datetime.fromtimestamp(os.path.getmtime(self.filename))

    def get_type(self):
        return self.__TYPE


class FileSourceStream:
    def __init__(self, dir, last_id=None) -> None:
        self.data = []
        self.index = 0
        for (dirpath, dirnames, filenames) in walk(dir):
            found = not last_id
            for filename in filenames:
                source_id = path.join(dirpath, filename)
                if filename.upper().endswith('.JPG') or filename.upper().endswith('.JPEG'):
                    if found:
                        self.data.append(source_id)
                    elif source_id == last_id:
                        found = True
                    else:
                        print("Skip persisted", source_id)
                else:
                    print("Skip", source_id)

    def next(self):
        if self.index < len(self.data):
            result = self.data[self.index]
            self.index += 1
            return FileSource(result)
        else:
            return None
