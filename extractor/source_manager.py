import file_source
from file_source import FileSource


def get(source_id, source_type):
    if source_type == "file":
        return FileSource(source_id)
    else:
        return None
