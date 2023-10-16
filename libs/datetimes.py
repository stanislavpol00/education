from dateutil.parser import parse


def to_datetime(value):
    datetime_object = parse(value)

    datetime_object = datetime_object.astimezone()

    return datetime_object
