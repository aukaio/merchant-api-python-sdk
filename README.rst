=================
mcash-mapi-client
=================

A SDK used to make communication with mCASH's merchant API easier. A basic usage example is shown in `mapi_client_example`.

Before using this client
------------------------

* Be aware that this client is in beta. Backwards incompatible changes should not occur, but updates might be frequent. Comments and pull requests are welcome.
* Make sure you are familiar with the documentation, found at: `<http://dev.mca.sh/merchant/>`_. Consider reading the tutorials at `<http://dev.mca.sh/tutorials/>`_.
* Register as a merchant at `<https://my.mca.sh/ssp/merchant/>`_

Usage
-----
MapiClient is the main class and can be found in `mapi_client`. It's constructor takes 4 required arguments:

* mcash_merchant: Your merchant id, received while registering.
* mcash_user: Your merchant user, added in the SSP.
* base_url: The base url to use. For production this is `<http://api.mca.sh/>`_. The URL's to use for testing can be found at `<http://dev.mca.sh/>`_.
* auth: The authentication method to use. Accepts one of the classes defined in `auth`.  See the 'Auth' section for more information.

After being instantiated with these arguments, the client is ready to use. All functionality is provided as member methods of the MapiClient class.

Auth
^^^^
The merchant API supports 3 authentication levels:

* Open (no authentication)
* Secret
* RSA

These are represented in the merchant API client as classes in the `auth` file. When passed as an argument to the MapiClient during instantiation, authentication will be automatically applied to every request.


License
-------
| Copyright (C) 2014 mCASH Norge AS
| 
| Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
| 
| The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
| 
| THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
