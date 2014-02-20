''' Creates a merchant_user on the testbed.
'''

from auth import RSA_SHA256Auth
import requests
import json
import random
import sys
import httplib
from optparse import OptionParser
from Crypto.PublicKey import RSA


def gen_rsa_key_pair_files(merchant_id, merchant_user):
    RSAkey = RSA.generate(1024)
    private = RSA.generate(1024)
    public = private.publickey()
    fh = open(merchant_id + '_' + merchant_user + '_private.pem', 'w')
    fh.write(private.exportKey())
    fh.close()
    fh = open(merchant_id + '_' + merchant_user + '_public.pem', 'w')
    fh.write(public.exportKey())
    fh.close()


def create_merchant_user(
        my_testbed_token, integrator_pem_file, merchant_id, merchant_user):
    url_base = 'https://mcashtestbed.appspot.com'
    headers = {
        'Accept': 'application/vnd.mcash.api.merchant.v1+json',
        'Content-Type': 'application/json',
        'X-Testbed-Token': my_testbed_token,
        'X-Mcash-Merchant': merchant_id,
        'X-Mcash-Integrator': 'test_integrator'
    }

    print "setting up a RSA auth session with integrator RSA key"
    s = requests.Session()
    s.auth = RSA_SHA256Auth(integrator_pem_file)
    # from this point all requests through s use rsa auth, eg.:

    print "creating user RSA key pair files"
    gen_rsa_key_pair_files(merchant_id, merchant_user)
    fh = open(merchant_id + '_' + merchant_user + '_public.pem', 'r')
    pubkey = fh.read()
    fh.close()

    print "Creating a merchant_user.."
    payload = {
        'id': merchant_user,
        'roles': ['superuser'],
        'pubkey': pubkey
    }
    req = requests.Request("POST",
                           url_base + '/merchant/v1/user/',
                           data=json.dumps(payload),
                           headers=headers
                           )

    s2 = s.prepare_request(req)
    r = s.send(s.prepare_request(req))
    print "r.status_code =", r.status_code, " ", httplib.responses[r.status_code]
    assert r.status_code == 201, "Expected r.status_code to be 201"
