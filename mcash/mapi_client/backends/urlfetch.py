from ..mapi_response import MapiResponse
import json

from google.appengine.api import urlfetch

__all__ = ["UrlFetchFramework"]


class UrlFetchFramework(object):
    def dispatch_request(self, method, url, body, headers, auth):
        method, url, headers, body = auth(method, url, headers, body)

        payload = {}
        if body is not None:
            for key, value in body.iteritems():
                if value is not None:
                    payload.update({key: value})
        res = urlfetch.fetch(url=url,
                             payload=json.dumps(payload),
                             method=method,
                             headers=headers)
        return MapiResponse(res.status_code, res.headers, res.content)
