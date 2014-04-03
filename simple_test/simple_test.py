'''This file is provided as is, as an example of how some mcash merchant API
   calls look like. This file may change at anytime, without notification.
'''

import sys
from optparse import OptionParser
from create_merchant import create_merchant
from create_merchant_user import create_merchant_user
from rsa_auth_merchant_simple_test import rsa_auth_merchant_simple_test


def simple_test(my_testbed_token, integrator_name, integrator_rsa_file):
    merchant_id = create_merchant(my_testbed_token,
                                  integrator_name)
    merchant_user = "codemonkey"  # for example
    create_merchant_user(my_testbed_token,
                         integrator_rsa_file,
                         merchant_id,
                         merchant_user
                         )
    rsa_auth_merchant_simple_test(merchant_id,
                                  merchant_user,
                                  merchant_id + '_' +
                                  merchant_user + '_private.pem',
                                  my_testbed_token
                                  )


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-i", "--integrator_name", dest="integrator_name",
                      help="set the integrator_name")
    parser.add_option("-k", "--keyfilename", dest="integrator_rsa_file",
                      help="set the integrator RSA private key file. Should be recieved in an email")
    parser.add_option("-t", "--testbed_token", dest="testbed_token",
                      help="set the testbed_token. Should be recieved in an email")
    (options, args) = parser.parse_args()

    if options.testbed_token and options.integrator_name and options.integrator_rsa_file:
        simple_test(
            options.testbed_token,
            options.integrator_name,
            options.integrator_rsa_file)
    else:
        print "All command line options not given. Exiting.."
        parser.print_help()
        sys.exit(1)
