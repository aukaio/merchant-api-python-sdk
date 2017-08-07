from mcash import mapi_client
from requests import HTTPError
from random import choice
from string import ascii_lowercase


mapiclient = mapi_client.MapiClient(
    # RSA encryption is preferred
    auth=mapi_client.RsaSha256Auth('tests/testkey'),
    mcash_merchant='testmerchant2',  # The merchant id we use
    mcash_user='admin',              # The user to use for our merchant
    additional_headers={
        'X-Testbed-Token':           # mcash testbed needs a token
        'KEG5SFpAIPjV53s0RUO-q4yIGPzMv5wJGCzLdrCxFpQ'
    },
)

testuser_id = None
testpos_id = None
lid = None
prid = None


def _get_random_str(n):
    """Returns a random string of length n
    """
    return "".join([choice(ascii_lowercase)
                    for x in xrange(n)])


def test_create_user():
    key = ("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCYU7TkLNe8bJbVG2hyseII59"
           "a7wxAXNqG6tymmKRiVjI5CPhQmpMOzqM/RCvLiqseqI43DlZtKZSumHAuPT+hE"
           "t4j3w7ZjdKB7MHhJiy9z/UNt4a15WQlj7hYYLB+ACeff+BlKXuTKE7db4X/wzr"
           "W54VgNnF7JXaJ/vOPHZXdAzPtB9ZTLpnIngP64KYSd12cToDJIVHdRUNhf6yun"
           "YRacnxZSHe8x3RTPYL9xRyHXACvyz/xdHNoQJQBFQpFKizEt80GrfblGQXn/IN"
           "xu4sakWXI01zwwj+g3TIcyNsuZQ54GFFpUY9pxxyjxwgkWDVIPZ3vQRE/RPInf"
           "RHvzp+1r")
    try:
        global testuser_id
        testuser_id = str(mapiclient.create_user(
            user_id="test-"+_get_random_str(8),
            roles=['user'],
            secret='supersecret',
            pubkey=key)['id'])
    except HTTPError as e:
        code = e.response.status_code
        assert code == 409


def test_update_user():
    key = ("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCYU7TkLNe8bJbVG2hyseII59"
           "a7wxAXNqG6tymmKRiVjI5CPhQmpMOzqM/RCvLiqYOLO43DlZtKZSumHAuPT+hE"
           "t4j3w7ZjdKB7MHhJiy9z/UNt4a15WQlj7hYYLB+ACeff+BlKXuTKE7db4X/wzr"
           "W54VgNnF7JXaJ/vOTHISISAFAKEKEYYOLOgP64KYSd12cToDJIVHdRUNhf6yun"
           "YRacnxZSHe8x3RTPYL9xRyHXACvyz/xdHNoQJQBFQpFKizEt80GrfblGQXn/IN"
           "xu4sakWXI01zwwj+g3TIcyNsuZQ54GFFpUY9pxxyjxwgkWDVIPZ3vQRE/RPInf"
           "RHvzp+1r")
    mapiclient.update_user(user_id=testuser_id,
                           roles=['superuser'],
                           secret='changedsecret',
                           pubkey=key)


def test_get_user():
    test_create_user()
    mapiclient.get_user('testuser')


def test_create_pos():
    try:
        global testpos_id
        testpos_id = str(mapiclient.create_pos(
            name="testname",
            pos_type='store',
            location={'latitude': 37.235065,
                      'longitude': -115.811117,
                      'accuracy': 25.00},
            pos_id="testpos")['id'])
    except HTTPError as e:
        code = e.response.status_code
        assert code == 409


def test_update_pos():
    try:
        mapiclient.update_pos(name=testpos_id,
                              pos_type='webshop',
                              location={'latitude': 37.235066,
                                        'longitude': -115.811116,
                                        'accuracy': 50.00},
                              pos_id=testpos_id)
    except HTTPError as e:
        code = e.response.status_code
        assert code == 409


def test_get_pos():
    mapiclient.get_pos(testpos_id)


def test_delete_pos():
    mapiclient.delete_pos(testpos_id)


def test_create_payment_request():
    global prid
    prid = str(mapiclient.create_payment_request(
        customer="testmerchant-alice",
        currency="nok",
        amount="12.00",
        allow_credit=False,
        pos_id=testpos_id,
        pos_tid="uniqueid",
        action="auth",
        expires_in=3600,
        display_message_uri="http://example.com/examplemessage",
        callback_uri="pusher:m-testchannel",
        additional_amount=21.00,
        additional_edit=True,
        text="Descriptional test")['id'])


def test_get_payment_request():
    mapiclient.get_payment_request(tid=prid)


def test_get_payment_request_outcome():
    mapiclient.get_payment_request_outcome(tid=prid)


def test_update_ticket():
    mapiclient.update_ticket(tid=prid)


def test_create_shortlink():
    return mapiclient.create_shortlink(
        callback_uri="pusher:m-testmerchant-testchannel")


def test_get_shortlink():
    _id = str(test_create_shortlink()['id'])
    mapiclient.get_shortlink(_id)


def test_update_payment_request():
    mapiclient.update_payment_request(
        tid=prid,
        action="abort",
        callback_uri="pusher:m-testchannel",
        display_message_uri="http://example.com/examplemessage")


def test_get_last_settlement():
    try:
        mapiclient.get_last_settlement()
    except HTTPError as e:
        code = e.response.status_code
        assert code == 404


def test_get_all_settlements():
    mapiclient.get_all_settlements()

#    def test_get_settlement():
#        mapiclient.get_settlement(_id)


def test_create_permission_request():
    _tid = _get_random_str(5)
    try:
        mapiclient.create_permission_request(
            customer="testmerchant-alice",
            pos_id=testpos_id,
            pos_tid=_tid,
            expires_in=2592000,
            scope="openid address profile phone email fodselsnummer")
    except HTTPError as e:
        code = e.response.status_code
        assert code == 409


def test_get_permission_request():
    _tid = _get_random_str(5)
    try:
        _id = str(mapiclient.create_permission_request(
            customer="testmerchant-alice",
            pos_id=testpos_id,
            pos_tid=_tid,
            expires_in=2592000,
            scope="openid address profile phone email fodselsnummer")['id']
        )
    except HTTPError as e:
        code = e.response.status_code
        assert code == 409
    mapiclient.get_permission_request(_id)


def test_get_permission_request_outcome():
    _tid = _get_random_str(5)
    try:
        _id = str(mapiclient.create_permission_request(
            customer="testmerchant-alice",
            pos_id=testpos_id,
            pos_tid=_tid,
            expires_in=2592000,
            scope="openid address profile phone email fodselsnummer")['id']
        )
    except HTTPError as e:
        code = e.response.status_code
        assert code == 409
    mapiclient.get_permission_request_outcome(_id)
