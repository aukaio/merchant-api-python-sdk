from setuptools import setup

VERSION = "1.0.0"

setup(
    name="mcash_mapi_client",
    version=VERSION,
    description="Thin python wrapper around mCASH's merchant api",
    author="mCASH Norge AS",
    author_email="sm@mcash.no",
    license="MIT",
    url="https://github.com/mcash/merchant-api-python-sdk",
    install_requires=["pycrypto>=2.6",
                      "requests>=2.2.1",
                      "voluptuous>=0.8.4",
                      "websocket-client>=0.12.0",
                      "pusherclient>=0.2.0",
                      "wsgiref>=0.1.2"],
    dependency_links=["https://github.com/ekulyk/PythonPusherClient/tarball/master#egg=pusherclient-0.2.0"],
    packages=["mapi_client"],
)
