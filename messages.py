""" Command messages. These are the only things that can be sent.
Inheriting object is to make the class a new style class. Just do it. """
# Setup messages:
class SetupWorld (object):
    def __init__(self, world, player_identity):
        self.world = world
        self.identity = player_identity

# In game messages:
class Sync (object):
    def __init__ (self, positions, velocities, accelerations):
        self.positions_dict = positions
        self.velocities_dict = velocities
        self.accelerations_dict = accelerations

class Accelerate (object):
    def __init__ (self, identity, acceleration_ratio):
        self.identity = identity
        self.acceleration_ratio = acceleration_ratio

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

class Bounce (object):
    def __init__(self, identity, orientations):
        self.identity = identity
        self.orientations = orientations

class GameOver (object):
    def __init__(self, winner):
        self.winner = winner
