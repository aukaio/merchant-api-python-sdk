import pusherclient
import logging
from time import sleep
from threading import Thread, Event

__all__ = ["PusherConnector"]


class PusherConnector(object):

    """A connector to pusher that is able to call callables when an event is
    received
    """
    def __init__(self, pusher_api_key, callback_chan, logger=None):
        """Constructor

        Arguments:
            pusher_api_key: the key to authenticate with pusher with
            callback_chan: the channel to use to receive callbacks
        """
        self.logger = logger or logging.getLogger(__name__)
        self.pusher_connected_listeners = []
        self.pos_callback_chan = callback_chan
        self.pusher = pusherclient.Pusher(pusher_api_key)
        self.pusher.connection.logger.setLevel(logging.WARNING)
        self.pusher.connection.bind('pusher:connection_established',
                                    self._pusher_connect_handler)
        self.pusher.connect()
        self.pusherthread_stop = Event()
        self.pusherthread = Thread(target=self._runForever,
                                   args=(self.pusherthread_stop,))

    def _pusher_connect_handler(self, data):
        """Event handler for the connection_established event. Binds the
        shortlink_scanned event
        """
        self.channel = self.pusher.subscribe(self.pos_callback_chan)
        for listener in self.pusher_connected_listeners:
            listener(data)

    def bind(self, event, handler):
        """Bind the handler so it gets called when the event is received

        Arguments:
            event: event to react to
            handler: handler to call when event is received
        """
        self.channel.bind(event, handler)

    def _runForever(self, stop_event):
        """Runs the main loop

        Arguments:
            stop_event: threading.Event() as a stop signal
        """
        while(not stop_event.is_set()):
            state = self.pusher.connection.state

            if (state is not "connecting" and
                    state is not "connected"):
                self.logger.warning(
                    "Pusher seems to be disconnected, trying to reconnect")
                self.pusher.connect()

            stop_event.wait(0.5)

    def stop(self):
        """Stops the pusherclient cleanly
        """
        self.pusherthread_stop.set()
        self.pusher.disconnect()

        # wait until pusher is down
        while self.pusher.connection.state is "connected":
            sleep(0.1)
        logging.info("shutting down pusher connector thread")
