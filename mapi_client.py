from requests import Request, Session
import json
from validation import validate_input
import logging
import traceback


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
            try:  # wrapped in a try so we can catch and print a stacktrace
                resp.raise_for_status()
            except:  # need to join lines from tb together here
                msg = ''.join('' + l for l in traceback.format_stack())
                self.logger.error(msg)
                raise
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

    def create(self, endpoint, **kwargs):
        """Create an entity at endpoint.
        """
        return self.do_req('POST',
                           self.base_url + '/' + endpoint + '/',
                           kwargs)

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

    def get_merchant(self, merchant_id):
        """Endpoint for retrieving info about merchants

        This endpoint supports retrieval of the information about a merchant
        that is mainly relevant to an integrator. Administration of the
        merchant resource is not part of the Merchant API as only the legal
        entity owning the merchant has access to do this using the SSP (Self
        Service Portal).

        Arguments:
            merchant_id -- Merchant id assigned by mCASH
        """
        return self.do_req('GET',
                           self.base_url + '/merchant/'
                           + merchant_id + '/').json()

    def get_merchant_lookup(self, lookup_id):
        """Perform a Merchant Lookup.

        Handle merchant lookup on secondary ID. This is endpoint can only be
        used by integrators.
        """
        return self.do_req('GET',
                           self.base_url + '/merchant_lookup/'
                           + lookup_id + '/').json()

    @validate_input
    def create_user(self, **kwargs):
        """Create user for the Merchant given in the X-Mcash-Merchant header.
        """
        return self.do_req('POST', self.base_url + '/user/', kwargs).json()

    @validate_input
    def update_user(self, user_id, **kwargs):
        """Update user

        Arguments:
            user_id -- User id of user to update
        """
        return self.do_req('PUT',
                           self.base_url + '/user/'
                           + user_id + '/', kwargs).json()

    def get_user(self, user_id):
        """Get user info

        Arguments:
            user_id -- User id of user to update
        """
        return self.do_req('GET',
                           self.base_url + '/user/'
                           + user_id + '/').json()

    @validate_input
    def create_pos(self, **kwargs):
        """Create POS resource
        """
        return self.do_req('POST', self.base_url + '/pos/', kwargs).json()

    def get_all_pos(self):
        """List all Point of Sales for merchant
        """
        return self._depaginate(self.base_url + '/pos/')

    @validate_input
    def update_pos(self, pos_id, **kwargs):
        """Update POS resource

        Arguments:
            pos_id -- POS id as chosen on registration
        """
        return self.do_req('PUT',
                           self.base_url + '/pos/'
                           + pos_id + '/', kwargs).json()

    def delete_pos(self, pos_id):
        """Delete POS

        Arguments:
            pos_id -- POS id as chosen on registration
        """
        return self.do_req('DELETE',
                           self.base_url + '/pos/'
                           + pos_id + '/').json()

    def get_pos(self, pos_id):
        """Retrieve POS info

        Arguments:
            pos_id -- POS id as chosen on registration
        """
        return self.do_req('GET',
                           self.base_url + '/pos/'
                           + pos_id + '/').json()

    @validate_input
    def create_payment_request(self, **kwargs):
        """Post payment request. The call is idempotent; that is, if one posts
        the same pos_id and pos_tid twice, only one payment request is created.

        Arguments:
            tid -- Transaction id assigned by mCASH
        """
        return self.do_req('POST', self.base_url + '/payment_request/',
                           kwargs).json()

    @validate_input
    def update_payment_request(self, tid, **kwargs):
        """Update payment request, reauthorize, capture, release or abort

        It is possible to update ledger and the callback URIs for a payment
        request. Changes are always appended to the open report of a ledger,
        and notifications are sent to the callback registered at the time of
        notification.

        Capturing an authorized payment or reauthorizing is done with the
        action field.

        The call is idempotent; that is, if one posts the same amount,
        additional_amount and capture_id twice with action CAPTURE, only one
        capture is performed. Similarly, if one posts twice with action CAPTURE
        without any amount stated, to capture the full amount, only one full
        capture is performed.

        Arguments:
            tid -- Transaction id assigned by mCASH
        """
        return self.do_req('PUT',
                           self.base_url + '/payment_request/'
                           + tid + '/', kwargs).json()

    def get_payment_request(self, tid):
        """Retrieve payment request info

        Arguments:
            tid -- Transaction id assigned by mCASH
        """
        return self.do_req('GET',
                           self.base_url + '/payment_request/'
                           + tid + '/').json()

    def get_payment_request_outcome(self, tid):
        """Retrieve payment request outcome

        Arguments:
            tid -- Transaction id assigned by mCASH
        """
        return self.do_req('GET',
                           self.base_url + '/payment_request/'
                           + tid + '/outcome/').json()

    @validate_input
    def update_ticket(self, tid, **kwargs):
        """If the customer should be granted an electronic ticket as a result
        of a successful payment, the merchant may (at any time) PUT ticket
        information to this endpoint. There is an ordered list of tickets; the
        merchant may PUT several times to update the list. The PUT overwrites
        any existing content, so if adding additional tickets one must remember
        to also include the tickets previously issued.

        So far the only code type supported is "string", meaning a text code
        that is displayed to the customer, however we will add QR code,
        barcodes etc. soon.  Please contact mCASH about supporting your
        barcode.
        """
        return self.do_req('PUT',
                           self.base_url + '/payment_request/'
                           + tid + '/ticket/', kwargs).json()

    @validate_input
    def create_shortlink(self, **kwargs):
        """Register new shortlink
        """
        return self.do_req('POST', self.base_url + '/shortlink/',
                           kwargs).json()

    def get_all_shortlinks(self):
        """List shortlink registrations
        """
        return self._depaginate(self.base_url + '/shortlink/')

    @validate_input
    def update_shortlink(self, shortlink_id, **kwargs):
        """Update existing shortlink registration

        Arguments:
            shortlink_id -- Shortlink id assigned by mCASH
        """
        return self.do_req('PUT',
                           self.base_url + '/shortlink/'
                           + shortlink_id + '/', kwargs).json()

    def delete_shortlink(self, shortlink_id):
        """Delete shortlink

        Arguments:
            shortlink_id -- Shortlink id assigned by mCASH
        """
        return self.do_req('DELETE',
                           self.base_url + '/shortlink/'
                           + shortlink_id + '/').json()

    def get_shortlinks(self, shortlink_id):
        """Retrieve registered shortlink info

        Arguments:
            shortlink_id -- Shortlink id assigned by mCASH
        """
        return self.do_req('GET',
                           self.base_url + '/shortlink/'
                           + shortlink_id + '/').json()

    def create_ledger(self):
        """Create a ledger
        """
        return self.do_req('POST',
                           self.base_url + '/ledger/').json()

    def get_all_ledgers(self):
        """List available ledgers
        """
        return self._depaginate(self.base_url + '/ledger/')

    @validate_input
    def update_ledger(self, ledger_id, **kwargs):
        """Update ledger info

        Arguments:
            ledger_id -- Ledger id assigned by mCASH
        """
        return self.do_req('PUT',
                           self.base_url + '/ledger/'
                           + ledger_id + '/', kwargs).json()

    def disable_ledger(self, ledger_id):
        """Disable ledger. It will still be used for payments that are
        currently in progress, but it will not be possible to create new
        payments with the ledger.

        Arguments:
            ledger_id -- Ledger id assigned by mCASH
        """
        return self.do_req('DELETE',
                           self.base_url + '/ledger/'
                           + ledger_id + '/').json()

    def get_ledger(self, ledger_id):
        """Get ledger info

        Arguments:
            ledger_id -- Ledger id assigned by mCASH
        """
        return self.do_req('GET',
                           self.base_url + '/ledger/'
                           + ledger_id + '/').json()

    def get_all_reports(self, ledger_id):
        """List reports on given ledger

        Arguments:
            ledger_id -- Ledger id assigned by mCASH
        """
        return self._depaginate(self.base_url + '/ledger/'
                                + ledger_id + '/report/')

    @validate_input
    def close_report(self, ledger_id, report_id, **kwargs):
        u"""Close Report

        When you PUT to a report, it will start the process of closing it. When
        the closing process is complete (i.e. when report.status == 'closed')
        mCASH does a POST call to callback_uri, if provided. This call will
        contain JSON data similar to when GETing the Report.

        Closing a report automatically open a new one.

        The contents of a GET
        /merchant/v1/ledger/<ledger_id>/report/<report_id>/ is included in
        callback if callback is a secure URI, otherwise the link itself is sent
        in callback.

        Arguments:
            ledger_id -- Id for ledger for report
            report_id -- Report id assigned by mCASH
        """
        return self.do_req('PUT',
                           self.base_url + '/ledger/'
                           + ledger_id + '/report/'
                           + report_id + '/', kwargs).json()

    def get_report(self, ledger_id, report_id):
        """Get report info

        Arguments:
            ledger_id -- Id for ledger for report
            report_id -- Report id assigned by mCASH
        """
        return self.do_req('GET',
                           self.base_url + '/ledger/'
                           + ledger_id + '/report/'
                           + report_id + '/').json()

    def get_last_settlement(self):
        """This endpoint redirects to the last Settlement

        Whenever a new Settlement is generated, this reference is automatically
        updated.

        Redirect latest Settlement
        """
        return self.do_req('GET', self.base_url + '/last_settlement/').json()

    def get_all_settlements(self):
        """List settlements
        """
        return self._depaginate(self.base_url + '/settlement/')

    def get_settlement(self, settlement_id):
        """Retrieve information regarding one settlement. The settlement
        contains detailed information about the amount paid out in the
        payout_details form. In case merchant has unsettled fees from previous
        settlements, mCASH will attempt to settle these before paying out. If
        there are still unsettled fees after settlement is done, this amount
        will be transferred to the next settlement, or billed by mCASH.

        Parameters:
            settlement_id -- The ID of the settlement to retrieve.
        """
        return self.do_req('GET',
                           self.base_url + '/settlement/'
                           + settlement_id + '/').json()

    @validate_input
    def create_permission_request(self, **kwargs):
        """Create permission request

        The call is idempotent; that is, if one posts the same pos_id and
        pos_tid twice, only one Permission request is created.
        """
        return self.do_req('POST',
                           self.base_url + '/permission_request/',
                           kwargs).json()

    def get_permission_request(self, rid):
        """See permission request info

        Arguments:
            rid -- Permission request id assigned my mCASH
        """
        return self.do_req('GET',
                           self.base_url + '/permission_request/'
                           + rid + '/').json()

    def get_permission_request_outcome(self, rid):
        """See outcome of permission request

        Arguments:
            rid -- Permission request id assigned my mCASH
        """
        return self.do_req('GET',
                           self.base_url + '/permission_request/'
                           + rid + '/outcome/').json()

    def get_all_status_codes(self):
        """Get all status codes
        """
        return self._depaginate(self.base_url + '/status_code/')

    def get_status_code(self, value):
        """Get status code
        """
        return self.do_req('GET',
                           self.base_url + '/status_code/'
                           + value + '/').json()
