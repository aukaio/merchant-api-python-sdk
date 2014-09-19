from ..mapi_response import MapiResponse
import json

from google.appengine.api import urlfetch

__all__ = ["UrlFetchFramework"]


class UrlFetchFramework(object):
    def dispatch_request(self, method, url, body, headers, auth):
        method, url, headers, data = auth(method, url, headers, body)
        res = urlfetch.fetch(url=url,
                             payload=data,
                             method=method,
                             headers=headers)
        return MapiResponse(res.status_code, res.headers, res.content)
