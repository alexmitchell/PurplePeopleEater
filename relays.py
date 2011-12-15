from utilities.messaging import Forum
from utilities.core import Task


# All classes in here interface with the forum in some way.


# Command messages. These are the only things that can be sent.
# Inheriting object is to make the class a new style class. Just do it.
class InitialWorld (object):
    def __init__(self, world):
        self.world = world

class FinishPregame (object):
    pass

class Eater (object):
    def __init__(self, new_eater, old_eater):
        self.new = new_eater
        self.old = old_eater



# Relays:
class Reflex (Task):
    """ The only relay that can change the world (data)."""
    # Reflex {{{1
    def __init__ (self, engine):
        Task.__init__ (engine)

    def setup (self, forum, world):
        self.world = world
        self.forum = forum 

        # set up subscriptions
        forum.subscribe(Eater, self.change_eater)

    def change_eater(self, message):
        self.world.change_eater(message.new, message.old)

    def update (self, time):
        pass

    def teardown (self):
        pass
    # }}}1

class Referee (Task):
    """ Watches game data. When necessary, sends info to server (through
    forum). Note: Does not change game data! """
    # Referee {{{1
    def setup (self):
        world = self.world = self.engine.get_world()
        forum = self.forum = self.engine.get_subscriber()

        # set up subscriptions

    def update (self, time):
        pass

    def end_game (self):
        # Figure out if the game should end.
        # If so, send game over message.
        pass

    def teardown (self):
        pass
    # }}}1

class PlayerRelay (Task):
    """ Listens to player input. Sends info to server (through forum).
    Note: Does not change game data! """
    # PlayerRelay {{{1
    def setup (self):
        world = self.world = self.engine.get_world()
        forum = self.forum = self.engine.get_subscriber()

        # set up subscriptions

    def update (self, time):
        pass

    def teardown (self):
        pass
    # }}}1

""" class AIRelay (Task):
        Listens to AI commands, sends info to the server (through forum).
        Note: ai runs only on the server.
        Note: Does not change game data! """



""" Old code
Subscription examples from old code.
    self.forum.subscribe('Ping', self.triggers.ping)
    self.forum.subscribe('Finish', self.triggers.finish)

# Each message is an instance of one of the following classes.
class Ping(object):
    pass
class Finish(object):
    pass

class Triggers:
    def __init__ (self, engine):
        self.engine = engine
        #self.world = world

    def setup (self):
        pass

    def update (self, time):
        pass

    def ping (self, message):
        #print message #### Not using message correctly!!!

    def finish (self, message)

    def teardown (self):
        pass

    #def pass_world???
    """
