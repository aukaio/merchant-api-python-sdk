import json

__all__ = ['MapiResponse']


class MapiResponse(object):
    def __init__(self, status, headers, content):
        self.status = status
        self.headers = headers
        self.content = content

    def json(self):
        return json.loads(self.content)

    def __iter__(self):
        yield self.status
        yield self.headers
        yield self.content
