from requests import Request, Session
import time
import json
from validation import validate_input


class mAPIClient(object):
    _default_headers = {
        'Accept': 'application/vnd.mcash.api.merchant.v1+json',
        'Content-Type': 'application/json',
    }

    def __init__(self,
                 auth,
                 callback_client,
                 base_url='https://mcashtestbed.appspot.com/merchant/v1',
                 mcash_merchant='',
                 mcash_user='',
                 additional_headers={}
                 ):
        # exit flag
        self.should_run = True
        self.base_url = base_url
        # take the callback client
        self.callback_client = callback_client
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

    def start(self):
        self.callback_client.start()
        while self.should_run:
            time.sleep(1)
            print("outer loop")

    def stop(self):
        self.callback_client.stop()
        self.should_run = False

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

        return self.session.send(self.session.prepare_request(req))

    def bind(self, event_name, callable):
        """Bind a received pusher event to a callable

        Arguments:
            event_name: name of the event to bind
            callable:   callable to bind the event to
        """
        try:
            self.callback_client.bind(event_name, callable)
        except:
            raise

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
        return self.do_req('POST', self.base_url + '/' + endpoint + '/', kwargs)

    @validate_input
    def update(self, endpoint, id, **kwargs):
        """Update the entity with id at endpoint
        """
        return self.do_req('PUT', self.base_url + '/' + endpoint + '/' + id + '/', kwargs)

    def get(self, endpoint, id=None):
        """Get the entity with id from endpoint
        """
        if id is None:
            resp = self._depaginate(self.base_url + '/' + endpoint + '/')
            return resp
        else:
            resp = self.do_req('GET', self.base_url + '/' + endpoint + '/' + id + '/')
            return json.loads(resp.text)

    def delete(self, endpoint, id):
        """Delete the entity with id at endpoint
        """
        return self.do_req('DELETE', self.base_url + '/' + endpoint + '/' + id + '/')
