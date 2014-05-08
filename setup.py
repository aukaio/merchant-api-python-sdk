from setuptools import setup

VERSION = "0.1.2"

setup(
    name="mcash-mapi-client",
    version=VERSION,
    description="Thin python wrapper around mCASH's merchant api",
    author="mCASH Norge AS",
    author_email="sm@mcash.no",
    license="MIT",
    url="https://github.com/mcash/merchant-api-python-sdk",
    install_requires=["pycrypto>=2.6",
                      "requests>=2.2.1",
                      "voluptuous>=0.8.4",
                      "wsgiref>=0.1.2"],
    extras_require={
        'mapi_client_example':  ["pusherclient>=0.2.0"]
    },
    packages=["mcash.mapi_client", "mcash"],
    namespace_packages=['mcash']
)
