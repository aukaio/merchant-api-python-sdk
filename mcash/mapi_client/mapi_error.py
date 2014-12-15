from mapi_response import MapiResponse

__all__ = ["MapiError"]


class MapiError(MapiResponse, Exception):
    def __init__(self, status, headers, content):
        MapiResponse.__init__(self, status, headers, content)
        Exception.__init__(self, status, headers, content)
