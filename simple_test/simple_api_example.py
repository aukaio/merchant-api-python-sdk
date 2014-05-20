'''This file is provided as is, as an example of how some mcash merchant API
   calls look like. This file may change at anytime, without notification.
'''

import sys
from optparse import OptionParser
from create_merchant import create_merchant
from create_merchant_user import create_merchant_user
from rsa_auth_merchant_simple_api_example import rsa_auth_merchant_simple_api_example
import urllib
import os


def simple_test(url_base, my_testbed_token, integrator_name, integrator_rsa_file):
    merchant_id = create_merchant(url_base,
                                  my_testbed_token,
                                  integrator_name)
    merchant_user = "codemonkey"  # for example
    create_merchant_user(url_base,
                         my_testbed_token,
                         integrator_rsa_file,
                         merchant_id,
                         merchant_user)

    rsa_auth_merchant_simple_api_example(url_base,
                                         merchant_id,
                                         merchant_user,
                                         merchant_id + '_' + merchant_user + '_private.pem',
                                         my_testbed_token)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-s", "--server", dest="server", default='mcashtestbed.appspot.com',
                      help="set the server")
    parser.add_option("-t", "--testbed_token", dest="testbed_token", default='none',
                      help="set the testbed_token")
    (options, args) = parser.parse_args()

    url_base = 'https://'+options.server
    if not os.path.isfile('test_integrator.pem'):
        urllib.urlretrieve(url_base+'/testbed/integrator_key/test_integrator.pem', 'test_integrator.pem')

    simple_test(
        url_base,
        options.testbed_token,
        'test_integrator',
        'test_integrator.pem')
