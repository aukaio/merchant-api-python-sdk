from requests import Request, Session
import json
from validation import validate_input
import logging


class mAPIClient(object):
    _default_headers = {
        'Accept': 'application/vnd.mcash.api.merchant.v1+json',
        'Content-Type': 'application/json',
    }

    def __init__(self,
                 auth,
                 base_url='https://mcashtestbed.appspot.com/merchant/v1',
                 mcash_merchant='',
                 mcash_user='',
                 additional_headers={},
                 logger=None
                 ):
        self.logger = logger or logging.getLogger(__name__)
        # exit flag
        self.base_url = base_url
        # save the merchant_id, we will use it for some callback values
        self.mcash_merchant = mcash_merchant
        # Start a new session
        self.session = Session()
        self.session.auth = auth
        self.session.headers.clear()
        user_info_headers = {
            'X-Mcash-Merchant': mcash_merchant,
            'X-Mcash-User': mcash_user,
        }
        self.session.headers.update(self._default_headers)
        self.session.headers.update(user_info_headers)
        self.session.headers.update(additional_headers)

    def do_req(self, method, url, args=None):
        """Used internally to send a request to the API, left public
        so it can be used to talk to the API more directly.
        """
        if args is not None:
            req = Request(method,
                          url=url,
                          data=json.dumps(args))
        else:
            req = Request(method,
                          url=url)

        resp = self.session.send(self.session.prepare_request(req))
        if resp.status_code / 100 is not 2:
            resp.raise_for_status()
        return resp

    def _depaginate(self, url):
        """GETs the url provided and traverses the 'next' url that's
        returned while storing the data in a list.
        """
        resp = self.do_req('GET', url)
        data = json.loads(resp.text)
        next_url = data['next']
        del data['next']
        del data['prev']
        key, items = data.popitem()
        while next_url is not None:
            resp = self.do_req('GET', next_url)
            data = json.loads(resp.text)
            next_url = data['next']
            del data['next']
            del data['prev']
            key, new_items = data.popitem()
            items += new_items
        return items

    @validate_input
    def create(self, endpoint, **kwargs):
        """Create an entity at endpoint.
        """
        return self.do_req('POST',
                           self.base_url + '/' + endpoint + '/',
                           kwargs)

    @validate_input
    def update(self, endpoint, _id, **kwargs):
        """Update the entity with id at endpoint
        """
        return self.do_req('PUT',
                           self.base_url + '/' + endpoint + '/' + _id + '/',
                           kwargs)

    def get(self, endpoint, _id=None):
        """Get the entity with _id from endpoint or all entities if _id is None
        """
        if _id is None:
            data = self._depaginate(self.base_url + '/' + endpoint + '/')
        else:
            data = self.do_req('GET',
                               self.base_url
                               + '/' + endpoint
                               + '/' + _id + '/').text
        return data

    def delete(self, endpoint, _id):
        """Delete the entity with id at endpoint
        """
        return self.do_req('DELETE',
                           self.base_url + '/' + endpoint + '/' + _id + '/')
