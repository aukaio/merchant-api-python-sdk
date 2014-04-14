merchant-api-python-sdk
=======================

A SDK used to make communication with mCASH's merchant API easier. A basic example is shown in 'mcash/mapi_client/mapi_client_example.py'.

## Usage
MapiClient is the main class and can be found in 'mcash/mapi_client/mapi_client.py'. It's constructor takes 4 required arguments:

* mcash_merchant: Your merchant id, received while registering.
* mcash_user: Your merchant user, added in the SSP.
* base_url: The base url to use. For production this is "http://api.mca.sh/". The URL's to use for testing can be found at http://dev.mca.sh/.
* auth: The authentication method to use. Accepts one of the classes defined in 'mcash/mapi_client/auth.py'

## Files and how to use them
| File                                 | Description   |
| ------------------------------------ | ------------- |
| mcash/mapi_client/mapi_client.py     | right-aligned |
| mcash/mapi_client/auth.py            | centered      |
| mcash/mapi_client/pusherconnector.py | are neat      |
