import pusherclient
import logging
from time import sleep
from threading import Thread, Lock


class PusherConnector(Thread):

    """A connector to pusher that is able to call callables when an event is
    received
    """
    def __init__(self, pusher_api_key, callback_chan):
        """Constructor

        Arguments:
            pusher_api_key: the key to authenticate with pusher with
            callback_chan: the channel to use to receive callbacks
        """
        super(PusherConnector, self).__init__()
        self.quitflag = False
        self.quitlock = Lock()
        self.pos_callback_chan = callback_chan
        self.pusher = pusherclient.Pusher(pusher_api_key)
        self.pusher.connection.logger.setLevel(logging.WARNING)
        self.pusher.connection.bind('pusher:connection_established',
                                    self.pusher_connect_handler)
        self.pusher.connect()

    def pusher_connect_handler(self, data):
        """Event handler for the connection_established event. Binds the
        shortlink_scanned event
        """
        self.channel = self.pusher.subscribe(self.pos_callback_chan)

    def bind(self, event, handler):
        for attempt in range(20):
            try:
                self.channel.bind(event, handler)
            except AttributeError:
                print("sleeping 2 seconds before retry")
                sleep(2)
                print("retry {}/20".format(attempt))
            except:
                raise
            else:
                break
        else:
            print("Binding failed :(")

    def run(self):
        """Runs the main loop
        """
        while True:
            with self.quitlock:
                if self.quitflag:
                    return

            sleep(1)

    def stop(self):
        """Stops the pusherclient thread
        """
        self.pusher.disconnect()
        with self.quitlock:
            self.quitflag = True
        logging.info("shutting down pusher connector thread")
