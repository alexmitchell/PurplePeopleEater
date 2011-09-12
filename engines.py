#used for debugging
import time
import sys

import network_settings
import triggers
#from world import World
#from game import Game

from utilities.core import Engine
from utilities.network import EasyServer
from utilities.network import EasyClient
from utilities.messaging import Forum


class ServerPregame (Engine):
    """ Gets the server ready to run the game: Sets up the network, connect to
    clients, set up the forum, and, in teardown, create the world. """
    
    # Consructor {{{1
    def __init__ (self, loop):
        Engine.__init__ (self, loop)

        host = network_settings.host
        port = network_settings.port
        seats = network_settings.seats
        callback = self.accept_callback
        self.server = EasyServer (host, port, seats, callback)

        self.forum = Forum ()

        self.world = None

    def setup (self):
        print 'Server setting up'
        self.server.setup()
        print 'Server ending setup'
    # }}}1

    # Update {{{1
    def update (self, time):
        self.server.accept()
        if self.server.full():
            self.finish()
            print 'Server ending update'

    # Methods {{{1
    def accept_callback(self, pipe):
        self.forum.connect(pipe)

    def successor (self):
        return ServerGame(self.loop, self.server, self.forum, self.world)
    
    def teardown (self):
        print 'Server tearing down'
        self.world = None
        #self.world = World()
        # setup world?
    # }}}1

class ServerGame (Engine):
    def __init__ (self, loop, server, forum, world):
        Engine.__init__ (self, loop)

        self.server = server
        self.forum = forum
        self.world = world
        #self. game = Game (world)

        self.triggers = Triggers

    def setup (self):
        print 'Server game setting up'
        self.forum.lock()
        self.forum.publish (Ping('hello!'))
        # setup game (Game is what changes world)
        # setup subscriptions
        # setup triggers
        # send world data to clients 

    def update (self, time):
        print 'Server game updating'
        self.finish()

        # update triggers
        # update forum
        # update game

    def successor (self):
        #return ServerPostgame(self.loop, self.world)
        return None 
    
    def teardown (self):
        print 'Server game tearing down'
        self.forum.disconnect()
        self.server.teardown()
        time.sleep(1)
        sys.exit()

# unfinished sever engines {{{1
class ServerPostgame (Engine):
    def __init__ (self, loop):
        Engine.__init__ (self, loop)

    def setup (self):
        # server closes before postgame....?
        pass

    def update (self, time):
        pass

    def teardown (self):
        pass
# }}}1

class ClientPregame (Engine):
    # Constructor {{{1
    def __init__ (self, loop):
        Engine.__init__ (self, loop)

        host = network_settings.host
        port = network_settings.port
        self.client = EasyClient (host, port)

        self.forum = Forum()
        
    def setup (self):
        print 'Client pregame setting up'
        self.client.setup()
        # setup forum

    # methods {{{1
    def update (self, time):
        print 'Client pregame updating'
        if self.client.ready():
            self.finish()
        else:
            self.client.setup()

    def successor (self):
        return ClientGame(self.loop, self.client, self.forum)
    
    def teardown (self):
        print 'Client pregame tearing down'
    # }}}1

class ClientGame (Engine):
    def __init__ (self, loop, client, forum):
        Engine.__init__ (self, loop)

        self.client = client
        self.forum = forum

        self.triggers = Triggers(self)

    def setup (self):
        print 'Client game setting up'

        # set up forum subscriptions
        self.forum.subscribe('Ping', self.triggers.ping)
        self.forum.subscribe('Finish', self.triggers.finish)
        self.forum.lock()

        # self.world = World()
        # receive world data from server using forum?

    def update (self, time):
        self.forum.deliver ()

    def successor (self):
        #return ClientPostgame(self.loop)
        return None
    
    def teardown (self):
        print 'Client game tearing down'
        self.forum.disconnect()
        self.client.teardown()
        time.sleep(1)
        sys.exit()

# unfinished client engines {{{1
class ClientPostgame (Engine):
    def __init__ (self, loop):
        Engine.__init__ (self, loop)

    def setup (self):
        pass

    def update (self, time):
        pass

    def teardown (self):
        pass
# }}}1
