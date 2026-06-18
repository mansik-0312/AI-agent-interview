from bson import ObjectId
from .response_mixin import CustomResponseMixin
from datetime import datetime
response = CustomResponseMixin()
from datetime import datetime
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

#helper function for serialize_datetime_fields
def serialize_datetime_fields(data):
    """
    Recursively serialize datetime fields in a dictionary to ISO format strings.
    This function handles nested dictionaries and lists.
    """
    if isinstance(data, dict):
        serialized = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                serialized[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, (dict, list)):
                serialized[key] = serialize_datetime_fields(value)
            else:
                serialized[key] = value
        return serialized
    elif isinstance(data, list):
        return [serialize_datetime_fields(item) for item in data]
    else:
        return data


#helper function for convert_objectid_to_str
def convert_objectid_to_str(obj):
    """
    Recursively convert ObjectId fields to strings in a dict or list.
    """
    if isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj


def convert_datetime_to_date(obj, date_format="%Y-%m-%d"):
    """
     Recursively convert datetime objects to formatted date string.
    """
    if isinstance(obj, datetime):
        return obj.strftime(date_format)
    elif isinstance(obj, dict):
        return {k: convert_datetime_to_date(v, date_format) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime_to_date(item, date_format) for item in obj]
    else:
        return obj

