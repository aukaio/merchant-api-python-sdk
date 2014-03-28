from requests import HTTPError
from random import choice
from string import ascii_lowercase

from mapi_client import mAPIClient
from auth import RSA_SHA256Auth


class TestmAPIClient(object):

    @classmethod
    def setup_class(self):
        # Set up the mAPI client
        self.mapiclient = mAPIClient(
            # RSA encryption is preferred
            auth=RSA_SHA256Auth('tests/testkey'),
            mcash_merchant='tes',   # The merchant id we use
            mcash_user='admin',             # The user to use for our merchant
            additional_headers={
                'X-Testbed-Token':          # mcash testbed needs a token
                'KEG5SFpAIPjV53s0RUO-q4yIGPzMv5wJGCzLdrCxFpQ'
            },
        )

    def get_random_str(self, n):
        """Returns a random string of length n
        """
        return "".join([choice(ascii_lowercase)
                        for x in xrange(n)])

    def test_create_user(self):
        key = ("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCYU7TkLNe8bJbVG2hyseII59"
               "a7wxAXNqG6tymmKRiVjI5CPhQmpMOzqM/RCvLiqseqI43DlZtKZSumHAuPT+hE"
               "t4j3w7ZjdKB7MHhJiy9z/UNt4a15WQlj7hYYLB+ACeff+BlKXuTKE7db4X/wzr"
               "W54VgNnF7JXaJ/vOPHZXdAzPtB9ZTLpnIngP64KYSd12cToDJIVHdRUNhf6yun"
               "YRacnxZSHe8x3RTPYL9xRyHXACvyz/xdHNoQJQBFQpFKizEt80GrfblGQXn/IN"
               "xu4sakWXI01zwwj+g3TIcyNsuZQ54GFFpUY9pxxyjxwgkWDVIPZ3vQRE/RPInf"
               "RHvzp+1r")
        try:
            self.mapiclient.create_user(user_id='testuser',
                                        roles=['user'],
                                        secret='supersecret',
                                        pubkey=key)
        except HTTPError as e:
            code = e.response.status_code
            assert code == 409

    def test_update_user(self):
        key = ("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCYU7TkLNe8bJbVG2hyseII59"
               "a7wxAXNqG6tymmKRiVjI5CPhQmpMOzqM/RCvLiqYOLO43DlZtKZSumHAuPT+hE"
               "t4j3w7ZjdKB7MHhJiy9z/UNt4a15WQlj7hYYLB+ACeff+BlKXuTKE7db4X/wzr"
               "W54VgNnF7JXaJ/vOTHISISAFAKEKEYYOLOgP64KYSd12cToDJIVHdRUNhf6yun"
               "YRacnxZSHe8x3RTPYL9xRyHXACvyz/xdHNoQJQBFQpFKizEt80GrfblGQXn/IN"
               "xu4sakWXI01zwwj+g3TIcyNsuZQ54GFFpUY9pxxyjxwgkWDVIPZ3vQRE/RPInf"
               "RHvzp+1r")
        self.mapiclient.update_user(user_id='testuser',
                                    roles=['superuser'],
                                    secret='changedsecret',
                                    pubkey=key)

    def test_get_user(self):
        self.test_create_user()
        self.mapiclient.get_user('testuser')

    def test_create_pos(self):
        try:
            self.mapiclient.create_pos(name='testpos',
                                       pos_type='store',
                                       location={'latitude': 37.235065,
                                                 'longitude': -115.811117,
                                                 'accuracy': 25.00},
                                       pos_id='test_pos_id')
        except HTTPError as e:
            code = e.response.status_code
            assert code == 409

    def test_update_pos(self):
        try:
            self.mapiclient.create_pos(name='testpos',
                                       pos_type='webshop',
                                       location={'latitude': 37.235066,
                                                 'longitude': -115.811116,
                                                 'accuracy': 50.00},
                                       pos_id='test_pos_id')
        except HTTPError as e:
            code = e.response.status_code
            assert code == 409

    def test_delete_pos(self):
        self.test_create_pos()
        self.mapiclient.delete_pos('test_pos_id')

    def test_get_pos(self):
        self.test_create_pos()
        self.mapiclient.get_pos('test_pos_id')

    def test_create_payment_request(self):
        return self.mapiclient.create_payment_request(
            customer="testmerchant-alice",
            currency="nok",
            amount="12.00",
            allow_credit=False,
            pos_id="test_pos_id",
            pos_tid="uniqueid",
            action="auth",
            expires_in=3600,
            # ledger='testledger',
            display_message_uri="http://example.com/yolo",
            callback_uri="pusher:m-testchannel",
            additional_amount=21.00,
            additional_edit=True,
            text="yolothisisatext")

    def test_update_payment_request(self):
        _lid = str(self.test_create_ledger()['id'])
        _pid = str(self.test_create_payment_request()['id'])
        self.mapiclient.update_payment_request(
            tid=_pid,
            action="abort",
            ledger=_lid,  # TODOFIXMEYOLO create ledger first
            callback_uri="pusher:m-testchannel",
            display_message_uri="http://example.com/yolo")

    def test_get_payment_request(self):
        _id = str(self.test_create_payment_request()['id'])
        self.mapiclient.get_payment_request(tid=_id)

    def test_get_payment_request_outcome(self):
        _id = str(self.test_create_payment_request()['id'])
        self.mapiclient.get_payment_request_outcome(tid=_id)

    def test_update_ticket(self):
        _id = str(self.test_create_payment_request()['id'])
        self.mapiclient.update_ticket(tid=_id)

    def test_create_shortlink(self):
        return self.mapiclient.create_shortlink(callback_uri="pusher:m-yolo",
                                                description="swagsterlink")

    def test_get_shortlink(self):
        _id = str(self.test_create_shortlink()['id'])
        self.mapiclient.get_shortlink(_id)

    def test_create_ledger(self):
        return self.mapiclient.create_ledger(currency='NOK')

    def test_get_all_ledgers(self):
        self.mapiclient.get_all_ledgers()

    def test_update_ledger(self):
        _id = str(self.test_create_ledger()['id'])
        self.mapiclient.update_ledger(ledger_id=_id)

    def test_disable_ledger(self):
        _id = str(self.test_create_ledger()['id'])
        self.mapiclient.disable_ledger(ledger_id=_id)

    def test_get_ledger(self):
        _id = str(self.test_create_ledger()['id'])
        self.mapiclient.get_ledger(ledger_id=_id)

    def test_get_all_reports(self):
        _id = str(self.test_create_ledger()['id'])
        return self.mapiclient.get_all_reports(ledger_id=_id)

#    def test_close_report(self):
#        _lid = str(self.test_create_ledger()['id'])
#        _rid = str(self.test_get_all_reports())
#        self.mapiclient.close_report(ledger_id=_lid,
#                                     report_id=_rid,
#                                     callback_uri="pusher:m-yolo")

#    def test_get_report(self):
#        pass

    def test_get_last_settlement(self):
        try:
            self.mapiclient.get_last_settlement()
        except HTTPError as e:
            code = e.response.status_code
            assert code == 404

    def test_get_all_settlements(self):
        self.mapiclient.get_all_settlements()

#    def test_get_settlement(self):
#        self.mapiclient.get_settlement(_id)

    def test_create_permission_request(self):
        _tid = self.get_random_str(5)
        try:
            self.mapiclient.create_permission_request(
                customer="testmerchant-alice",
                pos_id="test_pos_id",
                pos_tid=_tid,
                expires_in=2592000,
                scope="openid address profile phone email fodselsnummer")
        except HTTPError as e:
            code = e.response.status_code
            assert code == 409

    def test_get_permission_request(self):
        _tid = self.get_random_str(5)
        try:
            _id = str(self.mapiclient.create_permission_request(
                customer="testmerchant-alice",
                pos_id="test_pos_id",
                pos_tid=_tid,
                expires_in=2592000,
                scope="openid address profile phone email fodselsnummer")['id'])
        except HTTPError as e:
            code = e.response.status_code
            assert code == 409
        self.mapiclient.get_permission_request(_id)

    def test_get_permission_request_outcome(self):
        _tid = self.get_random_str(5)
        try:
            _id = str(self.mapiclient.create_permission_request(
                customer="testmerchant-alice",
                pos_id="test_pos_id",
                pos_tid=_tid,
                expires_in=2592000,
                scope="openid address profile phone email fodselsnummer")['id'])
        except HTTPError as e:
            code = e.response.status_code
            assert code == 409
        self.mapiclient.get_permission_request_outcome(_id)
