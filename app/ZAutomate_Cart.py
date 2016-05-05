import time
from ZAutomate_Player_madao import Player

class Cart(object):
    cart_id = None
    title = None
    issuer = None
    cart_type = None

    _player = None

    def __init__(self, cart_id, title, issuer, cart_type, filename):
        # TODO: mock ZAutoLib in development
        filename = "test/test.mp3"

        self.cart_id = cart_id
        self.title = title
        self.issuer = issuer
        self.cart_type = cart_type

        try:
            self._player = Player(filename)
        except IOError:
            print time.asctime() + " :=: Cart :: could not load audio file " + filename

    def is_playable(self):
        return self._player is not None

    def is_playing(self):
        return self._player.is_playing()

    def seek_to_front(self):
        self._player.seek_to_front()

    def start(self, callback=None):
        print time.asctime() + " :=: Cart :: Start :: " + self.title + " - " + self.issuer
        self._player.play(callback)

    def stop(self):
        print time.asctime() + " :=: Cart :: Stop :: " + self.issuer + " - " + self.title
        self._player.stop()

    def _get_meter_data(self):
        return (self._player.time_elapsed(), self._player.length(), self.title, self.issuer, self.cart_id, self.cart_type)
