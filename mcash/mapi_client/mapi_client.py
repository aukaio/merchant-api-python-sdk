import json
from auth import OpenAuth
from validation import validate_input
import logging
from mapi_response import MapiResponse
from backends.requestsframework import RequestsFramework
from mapi_error import MapiError

from poster.encode import multipart_encode
from poster.encode import MultipartParam



__all__ = ["MapiClient"]


class MapiClient(object):
    _default_headers = {
        'Accept': 'application/vnd.mcash.api.merchant.v1+json',
        'Content-Type': 'application/json',
    }

    def __init__(self,
                 base_url,
                 auth,
                 mcash_merchant,
                 mcash_user=None,
                 mcash_integrator=None,
                 additional_headers=None,
                 logger=None
                 ):
        """
        TODO: we need some explanations of the arguments here
        """

        if additional_headers is None:
            additional_headers = {}

        self.backend = RequestsFramework()
        self.auth = auth
        self.logger = logger or logging.getLogger(__name__)
        self.base_url = base_url
        # save the merchant_id, we will use it for some callback values
        self.mcash_merchant = mcash_merchant
        if (mcash_user and mcash_integrator) or (not mcash_user and not mcash_integrator):
            raise ValueError("either mcash_user or mcash_integrator should be set")
        self.mcash_user = mcash_user
        self.mcash_integrator = mcash_integrator
        self.default_headers = self._default_headers.copy()
        self.default_headers.update(additional_headers)

    def get_headers(self, headers=None):
        if not headers:
            headers = {}
        h = self.default_headers.copy()
        h.update({
            'X-Mcash-Merchant': self.mcash_merchant,
        })

        if self.mcash_integrator:
            h['X-Mcash-Integrator'] = self.mcash_integrator
        else:
            h['X-Mcash-User'] = self.mcash_user

        h.update(headers)
        return h

    def do_req(self, method, url, body=None, headers=None, status=None):
        """Used internally to send a request to the API, left public
        so it can be used to talk to the API more directly.
        """
        if body is None:
            body = ''
        else:
            body = json.dumps(body)
        res = self.backend.dispatch_request(method=method,
                                            url=url,
                                            body=body,
                                            headers=self.get_headers(headers),
                                            auth=self.auth)
        if not isinstance(res, MapiResponse):
            res = MapiResponse(*res)
        if status is None and res.status // 100 != 2:
            raise MapiError(*res)
        return res

    def _depagination_generator(self, url):
        data = self.do_req('GET', url).json()
        yield data['uris']

        next_link = data.pop('next')
        while next_link is not None:
            data = self.do_req('GET', next_link).json()
            next_link = data.pop('next')
            yield data['uris']

    def _depaginate_all(self, url):
        """GETs the url provided and traverses the 'next' url that's
        returned while storing the data in a list. Returns a single list of all
        items.
        """
        items = []
        for x in self._depagination_generator(url):
            items += x
        return items

    def get_merchant(self, merchant_id):
        """Endpoint for retrieving info about merchants

        This endpoint supports retrieval of the information about a merchant
        that is mainly relevant to an integrator. Administration of the
        merchant resource is not part of the Merchant API as only the legal
        entity owning the merchant has access to do this using the SSP (Self
        Service Portal).

        Arguments:
            merchant_id:
                Merchant id assigned by mCASH
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
    def create_user(self, user_id,
                    roles=None, netmask=None,
                    secret=None, pubkey=None):
        u"""Create user for the Merchant given in the X-Mcash-Merchant header.

        Arguments:
            user_id:
                Identifier for the user
            roles:
                Role
            netmask:
                Limit user connections by netmask, for example 192.168.1.0/24
            secret:
                Secret used when authenticating with mCASH
            pubkey:
                RSA key used for authenticating by signing
        """
        arguments = {'id': user_id,
                     'roles': roles,
                     'netmask': netmask,
                     'secret': secret,
                     'pubkey': pubkey}
        return self.do_req('POST', self.base_url + '/user/', arguments).json()

    @validate_input
    def update_user(self, user_id,
                    roles=None, netmask=None,
                    secret=None, pubkey=None):
        """Update user. Returns the raw response object.

        Arguments:
            user_id:
                User id of user to update
            roles:
                Role
            netmask:
                Limit user connections by netmask, for example 192.168.1.0/24
            secret:
                Secret used when authenticating with mCASH
            pubkey:
                RSA key used for authenticating by signing
        """
        arguments = {'roles': roles,
                     'netmask': netmask,
                     'secret': secret,
                     'pubkey': pubkey}
        return self.do_req('PUT',
                           self.base_url + '/user/'
                           + user_id + '/', arguments)

    def get_user(self, user_id):
        """Get user info

        Arguments:
            user_id:
                User id of user to update
        """
        return self.do_req('GET',
                           self.base_url + '/user/'
                           + user_id + '/').json()

    @validate_input
    def create_pos(self, name, pos_type,
                   pos_id, location=None):
        """Create POS resource

        Arguments:
            name:
                Human-readable name of the POS, used for displaying payment
                request origin to end user
            pos_type:
                POS type
            location:
                Merchant location
            pos_id:
                The ID of the POS that is to be created. Has to be unique for
                the merchant
        """
        arguments = {'name': name,
                     'type': pos_type,
                     'id': pos_id,
                     'location': location}
        return self.do_req('POST', self.base_url + '/pos/', arguments).json()

    def get_all_pos(self):
        """List all Point of Sales for merchant
        """
        return self._depaginate_all(self.base_url + '/pos/')

    @validate_input
    def update_pos(self, pos_id, name, pos_type, location=None):
        """Update POS resource. Returns the raw response object.

        Arguments:
            pos_id:
                POS id as chosen on registration
            name:
                Human-readable name of the POS, used for displaying payment
                request origin to end user
            pos_type:
                POS type
            location:
                Merchant location
        """
        arguments = {'name': name,
                     'type': pos_type,
                     'location': location}
        return self.do_req('PUT',
                           self.base_url + '/pos/'
                           + pos_id + '/', arguments)

    def delete_pos(self, pos_id):
        """Delete POS

        Arguments:
            pos_id:
                POS id as chosen on registration
        """
        return self.do_req('DELETE',
                           self.base_url + '/pos/'
                           + pos_id + '/')

    def get_pos(self, pos_id):
        """Retrieve POS info

        Arguments:
            pos_id:
                POS id as chosen on registration
        """
        return self.do_req('GET',
                           self.base_url + '/pos/'
                           + pos_id + '/').json()

    @validate_input
    def create_payment_request(self, customer, currency, amount, allow_credit,
                               pos_id, pos_tid, action, ledger=None,
                               display_message_uri=None, callback_uri=None,
                               additional_amount=None, additional_edit=None,
                               text=None, expires_in=None):
        """Post payment request. The call is idempotent; that is, if one posts
        the same pos_id and pos_tid twice, only one payment request is created.

        Arguments:
            ledger:
                Log entries will be added to the open report on the specified
                ledger
            display_message_uri:
                Messages that can be used to inform the POS operator about the
                progress of the payment request will be POSTed to this URI if
                provided
            callback_uri:
                If provided, mCASH will POST to this URI when the status of the
                payment request changes, using the message mechanism described
                in the introduction. The data in the "object" part of the
                message is the same as what can be retrieved by calling GET on
                the "/payment_request/<tid>/outcome/" resource URI.
            customer:
                Customer identifiers include msisdn, scan token or access token
            currency:
                3 chars https://en.wikipedia.org/wiki/ISO_4217
            amount:
                The base amount of the payment
            additional_amount:
                Typically cash withdrawal or gratuity
            additional_edit:
                Whether user is allowed to additional amount for gratuity or
                similar
            allow_credit:
                Whether to allow credit payment for this payment request.
                Credit incurs interchange
            pos_id:
                The POS this payment request originates from, used for
                informing user about origin
            pos_tid:
                Local transaction id for POS. This must be unique for the POS
            text:
                Text that is shown to user when asked to pay. This can contain
                linebreaks and the text has to fit on smartphones screens.
            action:
                Action to perform, the main difference is what it looks like in
                App UI.
            expires_in:
                Expiration in seconds from when server received request
        """
        arguments = {'customer': customer,
                     'currency': currency,
                     'amount': amount,
                     'allow_credit': allow_credit,
                     'pos_id': pos_id,
                     'pos_tid': pos_tid,
                     'action': action,
                     'ledger': ledger,
                     'display_message_uri': display_message_uri,
                     'callback_uri': callback_uri,
                     'additional_amount': additional_amount,
                     'additional_edit': additional_edit,
                     'text': text,
                     'expires_in': expires_in}
        return self.do_req('POST', self.base_url + '/payment_request/',
                           arguments).json()

    @validate_input
    def update_payment_request(self, tid, currency=None, amount=None,
                               action=None, ledger=None, callback_uri=None,
                               display_message_uri=None, capture_id=None,
                               additional_amount=None, text=None, refund_id=None):
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
            ledger:
                Log entries will be added to the open report on the specified
                ledger
            display_message_uri:
                Messages that can be used to inform the POS operator about the
                progress of the payment request will be POSTed to this URI if
                provided
            callback_uri:
                If provided, mCASH will POST to this URI when the status of the
                payment request changes, using the message mechanism described
                in the introduction. The data in the "object" part of the
                message is the same as what can be retrieved by calling GET on
                the "/payment_request/<tid>/outcome/" resource URI.
            currency:
                3 chars https://en.wikipedia.org/wiki/ISO_4217
            amount:
                The base amount of the payment
            additional_amount:
                Typically cash withdrawal or gratuity
            capture_id:
                Local id for capture. Must be set if amount is set, otherwise
                capture_id must be unset.
            tid:
                Transaction id assigned by mCASH
            refund_id:
                Refund id needed when doing partial refund
            text:
                For example reason for refund.
            action:
                Action to perform.
        """
        arguments = {'ledger': ledger,
                     'display_message_uri': display_message_uri,
                     'callback_uri': callback_uri,
                     'currency': currency,
                     'amount': amount,
                     'additional_amount': additional_amount,
                     'capture_id': capture_id,
                     'action': action,
                     'text': text,
                     'refund_id': refund_id}
        arguments = {k: v for k, v in arguments.items() if v is not None}
        return self.do_req('PUT',
                           self.base_url + '/payment_request/'
                           + tid + '/', arguments)

    def get_payment_request(self, tid):
        """Retrieve payment request info

        Arguments:
            tid:
                Transaction id assigned by mCASH
        """
        return self.do_req('GET',
                           self.base_url + '/payment_request/'
                           + tid + '/').json()

    def get_payment_request_outcome(self, tid):
        """Retrieve payment request outcome

        Arguments:
            tid:
                Transaction id assigned by mCASH
        """
        return self.do_req('GET',
                           self.base_url + '/payment_request/'
                           + tid + '/outcome/').json()

    @validate_input
    def update_ticket(self, tid, tickets=None):
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

        Arguments:
            tickets:
                List of tickets to grant customer
        """
        arguments = {'tickets': tickets}
        return self.do_req('PUT',
                           self.base_url + '/payment_request/'
                           + tid + '/ticket/', arguments)

    @validate_input
    def create_shortlink(self, callback_uri=None,
                         description=None, serial_number=None):
        """Register new shortlink

        Arguments:
            callback_uri:
                URI called by mCASH when user scans shortlink
            description:
                Shortlink description displayed in confirmation dialogs
            serial_number:
                Serial number on printed QR codes. This field is only used when
                registering printed stickers issued by mCASH
        """
        arguments = {'callback_uri': callback_uri,
                     'description': description,
                     'serial_number': serial_number}
        return self.do_req('POST', self.base_url + '/shortlink/',
                           arguments).json()

    def get_shortlink_generator(self):
        """List shortlink registrations
        """
        depaginator = self._depagination_generator(self.base_url +
                                                   '/shortlink/')
        return depaginator

    def get_all_shortlinks(self):
        """List shortlink registrations
        """
        return self._depaginate_all(self.base_url + '/shortlink/')

    @validate_input
    def update_shortlink(self, shortlink_id, callback_uri=None,
                         description=None):
        """Update existing shortlink registration

        Arguments:
            shortlink_id:
                Shortlink id assigned by mCASH
        """
        arguments = {'callback_uri': callback_uri,
                     'description': description}
        return self.do_req('PUT',
                           self.base_url + '/shortlink/'
                           + shortlink_id + '/', arguments)

    def delete_shortlink(self, shortlink_id):
        """Delete shortlink

        Arguments:
            shortlink_id:
                Shortlink id assigned by mCASH
        """
        return self.do_req('DELETE',
                           self.base_url + '/shortlink/'
                           + shortlink_id + '/').json()

    def get_shortlink(self, shortlink_id):
        """Retrieve registered shortlink info

        Arguments:
            shortlink_id:
                Shortlink id assigned by mCASH
        """
        return self.do_req('GET',
                           self.base_url + '/shortlink/'
                           + shortlink_id + '/').json()

    @validate_input
    def create_ledger(self, currency, description=None):
        """Create a ledger
        """
        arguments = {'currency': currency,
                     'description': description}
        return self.do_req('POST',
                           self.base_url + '/ledger/', arguments).json()

    def get_all_ledgers(self):
        """List available ledgers
        """
        return self._depaginate_all(self.base_url + '/ledger/')

    @validate_input
    def update_ledger(self, ledger_id, description=None):
        """Update ledger info

        Arguments:
            ledger_id:
                Ledger id assigned by mCASH
            description:
                Description of the Ledger and it's usage
        """
        arguments = {'description': description}
        return self.do_req('PUT',
                           self.base_url + '/ledger/'
                           + ledger_id + '/', arguments)

    def disable_ledger(self, ledger_id):
        """Disable ledger. It will still be used for payments that are
        currently in progress, but it will not be possible to create new
        payments with the ledger.

        Arguments:
            ledger_id:
                Ledger id assigned by mCASH
        """
        return self.do_req('DELETE',
                           self.base_url + '/ledger/'
                           + ledger_id + '/')

    def get_ledger(self, ledger_id):
        """Get ledger info

        Arguments:
            ledger_id:
                Ledger id assigned by mCASH
        """
        return self.do_req('GET',
                           self.base_url + '/ledger/'
                           + ledger_id + '/').json()

    def get_all_reports(self, ledger_id):
        """List reports on given ledger

        Arguments:
            ledger_id:
                Ledger id assigned by mCASH
        """
        return self._depaginate_all(self.base_url + '/ledger/'
                                    + ledger_id + '/report/')

    @validate_input
    def close_report(self, ledger_id, report_id, callback_uri=None):
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
            ledger_id:
                Id for ledger for report
            report_id:
                Report id assigned by mCASH
            callback_uri:
                Callback URI to be called when Report has finished closing.
        """
        arguments = {'callback_uri': callback_uri}
        return self.do_req('PUT',
                           self.base_url + '/ledger/'
                           + ledger_id + '/report/'
                           + report_id + '/', arguments)

    def get_report(self, ledger_id, report_id):
        """Get report info

        Arguments:
            ledger_id:
                Id for ledger for report
            report_id:
                Report id assigned by mCASH
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
        return self._depaginate_all(self.base_url + '/settlement/')

    def get_settlement(self, settlement_id):
        """Retrieve information regarding one settlement. The settlement
        contains detailed information about the amount paid out in the
        payout_details form. In case merchant has unsettled fees from previous
        settlements, mCASH will attempt to settle these before paying out. If
        there are still unsettled fees after settlement is done, this amount
        will be transferred to the next settlement, or billed by mCASH.

        Parameters:
            settlement_id:
                The ID of the settlement to retrieve.
        """
        return self.do_req('GET',
                           self.base_url + '/settlement/'
                           + settlement_id + '/').json()

    @validate_input
    def create_permission_request(self, customer, pos_id, pos_tid, scope,
                                  ledger=None, text=None, callback_uri=None,
                                  expires_in=None):
        """Create permission request

        The call is idempotent; that is, if one posts the same pos_id and
        pos_tid twice, only one Permission request is created.
        """
        arguments = {'customer': customer,
                     'pos_id': pos_id,
                     'pos_tid': pos_tid,
                     'scope': scope,
                     'ledger': ledger,
                     'text': text,
                     'callback_uri': callback_uri,
                     'expires_in': expires_in}
        return self.do_req('POST',
                           self.base_url + '/permission_request/',
                           arguments).json()

    def get_permission_request(self, rid):
        """See permission request info

        Arguments:
            rid:
                Permission request id assigned my mCASH
        """
        return self.do_req('GET',
                           self.base_url + '/permission_request/'
                           + rid + '/').json()

    def get_permission_request_outcome(self, rid):
        """See outcome of permission request

        Arguments:
            rid:
                Permission request id assigned my mCASH
        """
        return self.do_req('GET',
                           self.base_url + '/permission_request/'
                           + rid + '/outcome/').json()

    def get_all_status_codes(self):
        """Get all status codes
        """
        return self._depaginate_all(self.base_url + '/status_code/')

    def get_status_code(self, value):
        """Get status code
        """
        return self.do_req('GET',
                           self.base_url + '/status_code/'
                           + value + '/').json()

    def upload_receipt(self, url, data):
        """Upload a receipt to the give url

        :param url:
        :param data:
        :return:
        """
        return self.upload_attachment(url=url, data=data, mime_type='application/vnd.mcash.receipt.v1+json')

    def upload_attachment(self, url, mime_type, data):
        data, headers = multipart_encode([MultipartParam('file', value=data, filename='filename', filetype=mime_type)])
        data = "".join(data)
        res = self.backend.dispatch_request(method='POST',
                                            url=url,
                                            body=data,
                                            headers=headers,
                                            auth=OpenAuth())
        return res
