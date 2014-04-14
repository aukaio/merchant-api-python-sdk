import base64
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from time import strftime

from requests.auth import AuthBase

__all__ = ["OpenAuth", "SecretAuth", "RsaSha256Auth"]


class OpenAuth(AuthBase):

    """Attaches no authentication to the given Request object."""

    def __call__(self, r):
        return r


class SecretAuth(AuthBase):

    """Attaches Authentication with secret token to
    the given Request object."""

    def __init__(self, secret):
        self.secret = secret

    def __call__(self, r):
        r.headers['Authorization'] = 'SECRET ' + self.secret
        return r


class RsaSha256Auth(AuthBase):

    """Attaches RSA authentication to the given Request object."""

    def __init__(self, privkey_path):
        self.privkey_path = privkey_path

    def __call__(self, r):
        r.headers['X-Mcash-Timestamp'] = self._get_timestamp()
        r.headers['X-Mcash-Content-Digest'] = self._get_sha256_digest(r.body)
        r.headers['Authorization'] = self._sha256_sign(r)
        return r

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

    def _sha256_sign(self, r):
        """Sign the request with SHA256.
        """
        with open(self.privkey_path, 'r') as fd:
            signer = PKCS1_v1_5.new(RSA.importKey(fd.read()))

        d = ''
        sign_headers = r.method.upper() + '|' + r.url + '|'
        for key, value in sorted(r.headers.items()):
            if key.startswith('X-Mcash-'):
                sign_headers += d + key.upper() + '=' + value
                d = '&'

        rsa_signature = base64.b64encode(
            signer.sign(SHA256.new(sign_headers)))

        return 'RSA-SHA256 ' + rsa_signature
