import json

from src.utils.exception_decorator import catch_exceptions


@catch_exceptions((TypeError,))
def serialize_json(data: dict) -> str:
    return json.dumps(data)


@catch_exceptions((TypeError,))
def deserialize_json(data: str) -> dict:
    return json.loads(data)
