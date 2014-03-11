''' Creates a merchant_id on the testbed.
    This is intended to script some work that today is manual on the testbed.
'''

import requests
import json
import random
import sys
import httplib


def create_merchant(testbed_token, integrator_name):
    '''creates a merchant and returns the merchant_id'''

    url_base = 'https://mcashtestbed.appspot.com'
    print 'Create a merchant on testbed'
    headers = {
        'Content-Type': 'application/json',
        'X-Testbed-Token': testbed_token,
        'X-Mcash-Integrator': 'test_integrator'
    }
    r = requests.post(
        url_base + '/testbed/merchant/',
        headers=headers
    )
    print "r.status_code =", r.status_code, " ", httplib.responses[r.status_code]
    assert r.status_code == 200, "Expected r.status_code to be 200"
    merchant_id = r.headers['x-mcash-merchant']
    print "created merchant with merchant_id = ", merchant_id
    return merchant_id
