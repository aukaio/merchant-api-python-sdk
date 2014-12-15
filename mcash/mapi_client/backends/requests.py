from ..mapi_response import MapiResponse

__all__ = ["RequestsFramework"]

class RequestsFramework(object):
    def dispatch_request(self, method, url, data, headers, auth):
        import requests
        method, url, headers, data = auth(method, url, headers, data)
        res = requests.request(method,
                               url,
                               data=data,
                               headers=headers,
                               auth=auth)
        return MapiResponse(res.status_code, res.headers, res.content)