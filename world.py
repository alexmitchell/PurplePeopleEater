import random

from kxgames.vector import Vector
from kxgames.sprites import *
import game_settings

class World:
    """ Stores all information for all game data. Does no logic. The update
    function is used to change time dependent data (timer, motion, etc). The
    server has the official version while the clients have close
    approximations. """
    # Constructor {{{1
    def __init__ (self):
        self.time_elapsed = 0
        self.map_size = game_settings.map_size

        self.owner_identity = None
        self.winner = None

        self.players = {}
        self.targets = {}

        self.eater_identities = []

        self.friction_coefficient = game_settings.friction_coefficient

    # Setup {{{1
    def setup (self, player_identities, target_identities):
        # Create players and targets with identities.
        for identity in player_identities:
            player = Player(self, identity)
            player.setup()
            player.set_position(self.random_position())
            self.players[identity] = player

        for identity in target_identities:
            target = Target(self, identity)
            target.setup()
            target.set_position(self.random_position())
            self.targets[identity] = target

        # Decide who are the eaters.
        eater_count = game_settings.eater_count
        self.eater_identities = random.sample(player_identities, eater_count)

    # Update {{{1
    def update (self, time):
        self.time_elapsed += time

        sprites = self.players.values() + self.targets.values()
        for sprite in sprites:
            sprite.update (time)

        """ 
        if not self.owner_identity == None:
            print 'My position: ', self.players[self.owner_identity].get_position()
        else:
            target_list = []
            for target in self.targets.values():
                target_list.append(target.get_position()) 
            print 'Target positions: ', target_list """

    # Methods {{{1
    def destroy_player (self, player_id):
        try:
            del self.players[player_id]
        except KeyError:
            pass

    def change_eater (self, new, old):
        try:
            self.eater_identities.remove(old)
        except ValueError:
            pass
        self.eater_identities.append(new)

    def set_owner_identity(self, owner_id):
        self.owner_identity = owner_id

    def random_position(self):
        return random.random() * self.map_size

    def teardown(self):
        pass

    # Attributes {{{1
    def get_map_size(self):return self.map_size
    def get_players(self): return self.players
    def get_targets(self): return self.targets
    def get_eater_identities(self): return self.eater_identities
    def get_owner_identity(self): return self.owner_identity
    # }}}1

class Token (Vehicle):
    # Constructor {{{1
    def __init__ (self, world, identity):
        Vehicle.__init__ (self)
        self.world = world
        self.identity = identity

        self.life = 1
        self.max_life = 1
        self.radius = 1

        self.last_attacker = None

    def setup(self):
        raise NotImplementedError

    # Update {{{1
    def update(self, time):
        Vehicle.update(self, time)

    # Methods {{{1
    def damage(self, value, attacker_identity):
        self.life -= value
        if self.life < 0: self.life = 0
        self.last_attacker = attacker_identity

    def heal(self, value):
        self.life += value
        if self.life > self.max_life: self.life = self.max_life

    def reset_life(self):
        self.life = self.max_life

    # Attributes {{{1
    def get_identity(self): return self.identity
    def get_life(self): return self.life
    def get_last_attacker(self): return self.last_attacker
    def get_radius(self): return self.radius
    # }}}1

class Player (Token):
    """  Provides identity handling for players. Eventually store special 
    abilities. """
    # Constructor {{{1
    def __init__ (self, world, identity):
        Token.__init__(self, world, identity)
        self.bite_damage = 0
        self.player_behavior = PlayerAcceleration()
    
    def setup (self):
        player_mass = game_settings.player_mass
        max_a = game_settings.maximum_acceleration
        max_v = game_settings.maximum_velocity

        Vehicle.setup (self,
                maximum_acceleration = max_a,
                maximum_velocity = max_v,
                mass = player_mass)

        self.life = self.max_life = game_settings.player_life
        self.bite_damage = game_settings.bite_damage
        self.radius = game_settings.player_radius

        self.player_behavior.setup(self)
        friction = self.world.friction_coefficient
        self.add_behavior(self.player_behavior)
        self.add_behavior(Friction(self, 1, friction))

    # Update and methods {{{1
    def update (self, time):
        Token.update(self, time)

    def get_bite_damage(self): return self.bite_damage
    def get_player_behavior(self): return self.player_behavior
    #}}}1

class Target (Token):
    """ Provides identity handling and timeouts for targets. Eventually store
    information on the type of targets. """
    # Constructor {{{1
    def __init__ (self, world, identity):
        Token.__init__ (self, world, identity)

        self.timeout = game_settings.target_timeout
        self.timer =  0

    def setup(self):
        Vehicle.setup(self)
        self.radius = game_settings.target_radius
    
    # Update, methods, and attributes. {{{1
    def update(self, time):
        Token.update(self, time)
        self.timer += time
    
    def reset_timer(self):
        self.timer = 0

    def get_timer(self): return self.timer
    def get_timeout(self): return self.timeout
    # }}}1

class PlayerAcceleration(BaseBehavior):
    def __init__(self):
        self.acceleration = Vector.null()

    def setup(self, sprite, weight=1):
        BaseBehavior.__init__(self, sprite, weight)
    
    def update(self):
        return self.acceleration, self.power

    def set_acceleration(self, new):
        self.last_delta_velocity = self.acceleration
        self.acceleration = new
