#used for debugging
import time
import sys

import network_settings
import relays
#from world import World
#from game import Game

from utilities.core import Engine
from utilities.network import EasyServer
from utilities.network import EasyClient
from utilities.messaging import Forum


class ServerPregame (Engine):
    """ Gets the server ready to run the game: Sets up the network, connect to
    clients, set up the forum. """
    
    # Consructor {{{1
    def __init__ (self, loop):
        Engine.__init__ (self, loop)

        host = network_settings.host
        port = network_settings.port
        seats = network_settings.seats
        callback = self.accept_callback
        self.server = EasyServer (host, port, seats, callback)

        self.forum = Forum ()

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
        return ServerGame(self.loop, self.server, self.forum)
    
    def teardown (self):
        print 'Server tearing down'
    # }}}1

class ServerGame (Engine):
    """ Sets up the game on the server then plays it. The server controls the 
    game logic and will send the results to clients. Eventually, the server 
    will run the AI too. """
    # Constructor {{{1
    def __init__ (self, loop, server, forum):
        Engine.__init__ (self, loop)

        # Initialize the basic services.
        self.server = server
        self.forum = forum
        self.world = World()
        #self.game = Game(world)

        # Initialize the relays.
        self.referee = relays.Referee()
        self.reflex = relays.Reflex()
        #self.ai_relay = relays.AIRelay()

        #self.tasks = (self.game, self.reflex, self.referee, self.ai_relay)
        self.tasks = (self.game, self.reflex, self.referee)

    def setup (self):
        print 'Server game setting up'
        # Set up services and relays
        for task in self.tasks:
            task.setup()

        self.forum.lock()

        #Send world data to clients
        #self.forum.publish (Ping('hello!'))

        #Somehow send start message!

    # Update {{{1
    def update (self, time):
        # Update the network and forum, primarily for incoming stuff.
        self.server.update()
        self.forum.deliver()

        # Update tasks.
        for task in self.tasks:
            task.update (time)

        ## Necessary? ##
        # Update the forum and network, primarily for outgoing stuff.
        self.forum.deliver()
        self.server.update()

    # Methods {{{1
    def successor (self):
        #return ServerPostgame(self.loop)
        return None
    
    def teardown (self):
        print 'Server game tearing down'
        for task in self.tasks:
            task.teardown()
        self.forum.disconnect()
        #self.forum.teardown()
        self.server.teardown()
        self.world.teardown()
        time.sleep(1)
# }}}1

class ServerPostgame (Engine):
    # Is not used. Exists just in case a use comes up.
    # Postgame {{{1
    def __init__ (self, loop):
        Engine.__init__ (self, loop)

    def setup (self):
        pass

    def update (self, time):
        self.finish()

    def teardown (self):
        pass
# }}}1




class ClientPregame (Engine):
    # Sets up the network and forum for the client.
    # Constructor {{{1
    def __init__ (self, loop):
        Engine.__init__ (self, loop)

        host = network_settings.host
        port = network_settings.port
        self.client = EasyClient (host, port)

        self.forum = Forum()
        
    def setup (self):
        pass

    # Methods {{{1
    def update (self, time):
        print 'Client pregame updating'
        if self.client.ready():
            self.forum.connect (self.client)
            self.finish()
        else:
            self.client.setup()

    def successor (self):
        return ClientGame(self.loop, self.client, self.forum)
    
    def teardown (self):
        pass
    # }}}1

class ClientGame (Engine):
    """ Plays the game. Does not have any game logic. It send player input to
    the server which will eventually tell the client's game what to do. """
    # Constructor {{{1
    def __init__ (self, loop, client, forum):
        Engine.__init__ (self, loop)

        # Initialize basic services.
        self.client = client
        self.forum = forum
        self.world = World()
        self.gui = None
        #self.gui = Gui(self)

        # Initialize the relays.
        self.reflex = relays.Reflex()
        self.player_relay = relays.PlayerRelay()

        self.tasks = (self.reflex, self.player_relay)

    def setup (self):
        print 'Client game setting up'

        for task in self.tasks:
            task.setup()
        #self.gui.setup()

        self.forum.lock()
    
    # Update {{{1
    def update (self, time):
        self.client.update()
        self.forum.deliver()

        for task in self.tasks:
            task.update (time)

        self.gui.update(time)

    # Methods {{{1
    def successor (self):
        return ClientPostgame(
                self.loop,
                self.forum,
                self.world,
                self.gui,
                self.tasks)
    
    def teardown (self):
        print 'Client game tearing down'
        self.forum.disconnect()
        self.client.teardown()
        time.sleep(1)
    # }}}1

class ClientPostgame (Engine):
    """ The game does not close immediately, waits for player to close it. 
    Allows the victor time to feel good about themselves. """
    # Postgame {{{1
    def __init__ (self, loop, forum, world, gui, tasks):
        Engine.__init__ (self, loop)
        self.forum = forum
        self.world = world
        self.gui = gui
        self.tasks = tasks

    def setup (self):
        pass

    def update (self, time):
        self.forum.deliver()
        for task in self.tasks:
            task.update (time)
        # self.gui.update (time)
        
        # Somehow respond to a quit input.

    def teardown (self):
        self.gui.teardown()
        for task in self.tasks:
            task.teardown
        #self.forum.teardown()
        self.world.teardown()
        time.sleep(1)
# }}}1
