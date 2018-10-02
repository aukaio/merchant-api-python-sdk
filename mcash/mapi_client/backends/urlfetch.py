from ..mapi_response import MapiResponse
from ..mapi_error import MapiError
import json
import logging

from google.appengine.api import urlfetch

__all__ = ["UrlFetchFramework"]


class UrlFetchFramework(object):
    def dispatch_request(self, method, url, body, headers, auth):
        method, url, headers, data = auth(method, url, headers, body)

        payload = {}
        if type(data) == dict:
            for key, value in data.iteritems():
                if value is not None:
                    payload.update({key: value})
            data = json.dumps(payload)

        try:
            res = urlfetch.fetch(url=url,
                                payload=data,
                                method=method,
                                deadline=60,
                                follow_redirects=False,
                                headers=headers)
            return MapiResponse(res.status_code, res.headers, res.content)
        except urlfetch.DownloadError as e:
            # Wrap in MapiError -- client code shouldn't have to
            # worry about URLFetch-specific exceptions
            logging.error('Unable to fetch %s', url)
            logging.error('%r', e)
            raise MapiError(None, None, None)
