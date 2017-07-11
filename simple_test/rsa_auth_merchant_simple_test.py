from auth import RSA_SHA256Auth
import requests
import json
import random
import sys
import httplib
from optparse import OptionParser


def rsa_auth_merchant_simple_test(
        merchant_id, merchant_user, pemfilename, testbed_token):

    print "setting up a RSA auth session with merchant_user private RSA key"
    s = requests.Session()
    s.auth = RSA_SHA256Auth(pemfilename)
    # from this point all requests through s use rsa auth, eg.:

    url_base = 'https://mcashtestbed.appspot.com'
    headers = {
        'Accept': 'application/vnd.mcash.api.merchant.v1+json',
        'Content-Type': 'application/json',
        'X-Mcash-Merchant': merchant_id,
        'X-Mcash-User': merchant_user,
        'X-Testbed-Token': testbed_token
    }

    print "checking if we have a point of sale"
    req = requests.Request("GET",
                           url_base + '/merchant/v1/pos/',
                           headers=headers
                           )
    r = s.send(s.prepare_request(req))
    print "r.status_code =", r.status_code, " ", httplib.responses[r.status_code]

    if len(r.json()[u'uris']) == 0:
        print "creating a POS (point of sale) with pos_id '1'..."
        payload = {
            "id": "1",
            "name": "Kasse 1",
            "type": "store"
        }
        req = requests.Request("POST",
                               url_base + '/merchant/v1/pos/',
                               data=json.dumps(payload),
                               headers=headers
                               )
        r = s.send(s.prepare_request(req))
        print "r.status_code =", r.status_code, " ", httplib.responses[r.status_code]

    print "requesting auth for a payment..."
    pos_tid = random.randint(0, sys.maxsize)
    payload = {
        "customer": merchant_id + "-alice",
        "pos_id": "1",
        "pos_tid": str(pos_tid),
        "action": "auth",
        "currency": "NOK",
        "amount": "100.00",
        "additional_amount": "0",
        "additional_edit": False,
        "allow_credit": False,
        "expires_in": 21600,
        "text":
        "Thanks for your business here at Acme Inc! \nYour payment is being processed.",
        "display_message_uri": "https://www.acmeinc.com/pos/3/display/",
        "callback_uri": "https://www.acmeinc.com/pos/3/payment/h93d458qo4685/"
    }
    req = requests.Request("POST",
                           url_base + '/merchant/v1/payment_request/',
                           data=json.dumps(payload),
                           headers=headers
                           )
    r = s.send(s.prepare_request(req))
    print "r.status_code =", r.status_code, " ", httplib.responses[r.status_code]
    tid = r.json()['id']

    print "mocking costumer clicking pay in app"
    testbedheaders = {
        'X-Testbed-Token': testbed_token
    }
    url = url_base + \
        '/testbed/merchant/{merchant_id}/txn/{tid}/pay/'.format(merchant_id=merchant_id,
                                                                tid=tid)
    r = requests.post(url, data=json.dumps(payload), headers=testbedheaders)
    print "r.status_code =", r.status_code, " ", httplib.responses[r.status_code]
    assert r.status_code == 200, "Expected r.status_code to be 200, actually is %i = %s" % (
        r.status_code, httplib.responses[r.status_code])

    # or setup an eventlistner"
    print "Polling of /outcome/ while status <> auth"
    status = None
    while status != 'auth':
        print "  getting /outcome/ "
        req = requests.Request("GET",
                               url_base +
                               '/merchant/v1/payment_request/{tid}/outcome/'.format(tid=tid),
                               headers=headers)
        r = s.send(s.prepare_request(req))
        print "r.status_code =", r.status_code, " ", httplib.responses[r.status_code]
        assert r.status_code == 200, "Expected r.status_code to be 200, actually is %i = %s" % (
            r.status_code, httplib.responses[r.status_code])
        d = json.loads(r.text)
        status = d['status']
        print "status =", status

    print "Merchant capturing payment..."
    payload = {
        "action": "capture",
        "display_message_uri": "https://www.acmeinc.com/pos/3/display/",
        "callback_uri": "https://www.acmeinc.com/pos/3/payment/h93d458qo4685/"
    }
    req = requests.Request("PUT",
                           url_base +
                           '/merchant/v1/payment_request/{tid}/'.format(tid=tid),
                           data=json.dumps(payload),
                           headers=headers
                           )
    r = s.send(s.prepare_request(req))
    print "r.status_code =", r.status_code, " ", httplib.responses[r.status_code]
    assert r.status_code == 204, "Expected r.status_code to be 204"


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-u", "--user", dest="merchant_user",
                      help="set the user name")
    parser.add_option("-m", "--merchant", dest="merchant_id",
                      help="set the merchant id")
    parser.add_option("-f", "--filename", dest="pemfilename",
                      help="set RSA private key file. Should be a .pem file created when the user is created")
    parser.add_option("-t", "--testbed_token", dest="testbed_token",
                      help="set the testbed_token. Should be recieved in an email")
    (options, args) = parser.parse_args()

    if options.merchant_id and options.merchant_user and options.pemfilename and options.testbed_token:
        rsa_auth_merchant_simple_test(options.merchant_id,
                                      options.merchant_user,
                                      options.pemfilename,
                                      options.testbed_token)
    else:
        print "All command line options not given. Exiting.."
        sys.exit(1)
