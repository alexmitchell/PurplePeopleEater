""" Command messages. These are the only things that can be sent.
Inheriting object is to make the class a new style class. Just do it. """
# Setup messages:
class SetupWorld (object):
    def __init__(self, world, player_identity):
        self.world = world
        self.identity = player_identity

# In game messages:
class Bite (object):
    def __init__ (self, biter_identity):
        self.biter = biter_identity

class DestroyPlayer (object):
    def __init__(self, identity):
        self.identity = identity

class ChangeEater (object):
    def __init__(self, new_eater, old_eater):
        self.new = new_eater
        self.old = old_eater

class MoveTarget (object):
    def __init__(self, identity, position, reset=False):
        self.identity = identity
        self.position = position
        self.reset_life = reset

class GameOver (object):
    def __init__(self, winner):
        self.winner = winner

