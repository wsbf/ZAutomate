"""The cart module provides the Cart class.

Currently, carts and tracks are both represented by the "Cart"
class, but it may be better to have separate classes.

The Cart class uses the Player class to provide an audio stream. There
are three different implementations of the Player class, and Cart currently
uses madao.
"""
import time
from player_madao import Player

class Cart(object):
    """The Cart class contains the metadata and audio stream of a cart."""
    cart_id = None
    title = None
    issuer = None
    cart_type = None

    _player = None

    def __init__(self, cart_id, title, issuer, cart_type, filename):
        """Construct a Cart object.

        :param cart_id: cart ID
        :param title: cart title
        :param issuer: cart issuer
        :param cart_type: cart type
        :param filename: location of the cart file
        """
        self.cart_id = cart_id
        self.title = title
        self.issuer = issuer
        self.cart_type = cart_type

        # uncomment to mock ZAutoLib in development
        # filename = "test/test.mp3"

        try:
            self._player = Player(filename)
        except IOError:
            print time.asctime() + " :=: Cart :: could not load audio file " + filename

    def is_playable(self):
        """Get whether the cart has an audio stream."""
        return self._player is not None

    def is_playing(self):
        """Get whether the cart is currently playing."""
        return self._player.is_playing()

    def start(self, callback=None):
        """Play the cart's audio stream.

        :param callback: function to call if the stream ends
        """
        print time.asctime() + " :=: Cart :: Start :: " + self.issuer + " - " + self.title
        self._player.play(callback)

    def stop(self):
        """Stop the cart's audio stream."""
        print time.asctime() + " :=: Cart :: Stop :: " + self.issuer + " - " + self.title
        self._player.stop()

    def get_meter_data(self):
        """Get the meter data for the cart as a 4-tuple."""
        return (self._player.time_elapsed(), self._player.length(), self.title, self.issuer)
