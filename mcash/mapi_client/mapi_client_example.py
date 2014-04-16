from mcash import mapi_client
from mcash.mapi_client.pusherconnector import PusherConnector
import sys
import time
import logging
import signal
import pprint
import uuid
import json


class MapiClientExample(object):

    _pos_id = "winter_warming_stand_1"

    def handleSigINT(self, signal, frame):
        logging.info("got SIGINT, shutting down")
        # Give the callback client a chance to exit cleanly
        self.callback_client.stop()
        sys.exit(0)

    def shortlink_scanned(self, data):
        """Called when a shortlink_scanned event is received
        """
        # Inform log that we received an event
        self.logger.info("Received shortlink_scanned event")

        data = json.loads(data)
        customer_token = str(data['object']['id'])
        response = self.mapiclient.create_payment_request(
            customer=customer_token,
            currency="NOK",
            amount="20.00",
            allow_credit=True,
            pos_id=self._pos_id,
            pos_tid=str(uuid.uuid4()),
            action='auth',
            expires_in=90,
            callback_uri="pusher:m-winterwarming-pos_callback_chan",
            text='Have some hot chocolate!')
        self._tid = response['id']
        print(str(self._tid))

    def payment_authorized(self, data):
        self.logger.info("Received payment_authorized event")
        pprint.pprint(data)

        if self._tid is not None:
            self.mapiclient.update_payment_request(
                tid=str(self._tid),
                action='capture')

    def pusher_connected(self, data):
        """Called when the pusherclient is connected
        """
        # Inform user that pusher is done connecting
        self.logger.info("Pusherclient connected")

        # Bind the events we want to listen to
        self.callback_client.bind("payment_authorized",
                                  self.payment_authorized)
        self.callback_client.bind("shortlink_scanned",
                                  self.shortlink_scanned)

    def main(self):
        # set the log level to DEBUG, so we don't miss a thing
        self.logger = logging.getLogger('simpleexample')
        self.logger.setLevel(logging.DEBUG)

        # Handle interrupt signals cleanly
        signal.signal(signal.SIGINT, self.handleSigINT)

        # Set up a callback client, pusherclient in this case
        self.callback_client = PusherConnector(
            pusher_api_key='<your_pusher_api_key>',  # Your pusher API key
            callback_chan='m-winterwarming-pos_callback_chan',  # chan to use
            logger=self.logger)

        # Listen to the pusherclient connected signal, so we can use it to
        # later connect our other listeners
        self.callback_client.pusher_connected_listeners.append(
            self.pusher_connected)

        # Set up the mAPI client
        self.mapiclient = mapi_client.MapiClient(
            auth=mapi_client.RsaSha256Auth('rsakey'),  # RSA encryption is preferred
            mcash_merchant='exampleshop',   # The merchant id we use
            mcash_user='admin',             # The user to use for our merchant
            base_url='https://mcashtestbed.appspot.com/merchant/v1',
            additional_headers={
                'X-Testbed-Token':          # mcash testbed needs a token
                '<your_testbed_token>'
            },
            logger=self.logger
        )

        # Create a shortlink
        self.mapiclient.create_shortlink(
            callback_uri="pusher:m-winterwarming-pos_callback_chan")

        #uris, next_url, prev = self.mapiclient.get_shortlinks()
        pprint.pprint(self.mapiclient.get_all_shortlinks())

        # Sleep forever so we can keep listening to pusher signals
        while True:
            time.sleep(1)


if __name__ == '__main__':
    # Instantiate and run our example
    mapiclientexample = MapiClientExample()
    mapiclientexample.main()
