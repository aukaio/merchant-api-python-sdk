import base64
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from time import strftime

__all__ = ["OpenAuth", "SecretAuth", "RsaSha256Auth"]


class OpenAuth(object):
    """Attaches no authentication to the given Request object."""

    def __call__(self, method, url, headers, body):
        return method, url, headers, body


class SecretAuth(object):
    """Attaches Authentication with secret token to
    the given Request object."""

    def __init__(self, secret):
        self.secret = secret

    def __call__(self, method, url, headers, body):
        headers['Authorization'] = 'SECRET ' + self.secret
        return method, url, headers, body


class RsaSha256Auth(object):
    """Attaches RSA authentication to the given Request object."""

    def __init__(self, privkey):
        self.signer = PKCS1_v1_5.new(RSA.importKey(privkey))

    def __call__(self, method, url, headers, body):
        headers['X-Mcash-Timestamp'] = self._get_timestamp()
        headers['X-Mcash-Content-Digest'] = self._get_sha256_digest(body)
        headers['Authorization'] = self._sha256_sign(method, url, headers, body)
        return method, url, headers, body

    def _get_timestamp(self):
        """Return the timestamp formatted to comply with
        Merchant API expectations.
        """
        return str(strftime("%Y-%m-%d %H:%M:%S"))

    def _get_sha256_digest(self, content):
        """Return the sha256 digest of the content in the
        header format the Merchant API expects.
        """
        content_sha256 = base64.b64encode(SHA256.new(content).digest())
        return 'SHA256=' + content_sha256

    def _sha256_sign(self, method, url, headers, body):
        """Sign the request with SHA256.
        """
        d = ''
        sign_headers = method.upper() + '|' + url + '|'
        for key, value in sorted(headers.items()):
            if key.startswith('X-Mcash-'):
                sign_headers += d + key.upper() + '=' + value
                d = '&'

        rsa_signature = base64.b64encode(
            self.signer.sign(SHA256.new(sign_headers)))

        return 'RSA-SHA256 ' + rsa_signature
