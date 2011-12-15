from utilities.vector import Vector
from utilities.sprites import Sprite
import game_settings

class World:
    def __init__ (self):
        self.time_elapsed = 0

        self.owner = None

        self.players = {}
        self.targets = {}

        self.eaters = []

    def setup (self, player_identities, target_identities):
        """ Create players and targets with identities. """
        for identity in player_identities:
            player = Player()
            player.setup(identity)
            self.players[identity] = player

        for identity in target_identities:
            target = Object()
            target.setup(identity)
            self.targets[identity] = target

    def update (self, time):
        self.time_elapsed += time

        for sprite in self.players + self.targets:
            sprite.update (time):

    def destroy_player (self, player_id):
        del self.players[player_id]

    def change_eater (self, new, old):
        try:
            self.eaters.remove(old)
        except ValueError:
            pass
        self.eaters.append(new)


class Players (Sprite):
    """  Provides identity handling for players. Eventually store special 
    abilities. """
    def __init__ (self):
        Sprite.__init__ (self)
        self.identity = 0
    
    def setup (self, identity):
        Sprite.setup (self)
        self.identity = identity

    def update (self, time):
        Sprite.update(self, time)

class Target (Sprite):
    """ Provides identity handling and timeouts for targets. Eventually store
    information on the type of targets. """
    def __init__ (self):
        Sprite.__init__ (self)
        self.identity = 0
        self.timeout = game_settings.timeout
        self.timer =  0

    def setup(self, identity):
        Sprite.setup(self)
        self.identity = identity
    
    def update(self, time):
        Sprite.update(self, time)













