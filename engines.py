#used for debugging
import time
import sys

import network_settings
import game_settings
from gui import Gui
from messages import *
from world import World
from relays import *
import server_gui

from kxgames.core import Engine
from kxgames.network import PickleServer, PickleClient
from kxgames.messaging import Forum, SimpleSend, SimpleReceive


class ServerNetworkSetup (Engine):
    """ Gets the server ready to run the game: Sets up the network, connect to
    clients. """
    
    # Consructor {{{1
    def __init__ (self, loop):
        print 'S: Setting up server.'
        Engine.__init__ (self, loop)

        host = network_settings.host
        port = network_settings.port
        seats = network_settings.seats
        callback = self.server_full_callback
        self.server = PickleServer (host, port, seats, callback)

    def setup (self):
        self.server.open()

    # Update {{{1
    def update (self, time):
        self.server.accept()

    # Methods {{{1
    def server_full_callback(self, *pipes):
        self.exit_engine()

    def successor (self):
        print 'S: Server set up. All clients connected.'
        return ServerPregame(self.loop, self.server)
    
    def teardown (self):
        pass
    # }}}1

class ServerPregame (Engine):
    """ Sets up the world and creates client identities then sends both to each
    client. Eventually allow for users to modify the initial world settings
    plus personalizations like name or color. """
    # Constructor {{{1
    def __init__ (self, loop, server):
        print 'S: Begin pregame.'
        Engine.__init__(self,loop)
        self.server = server

        self.world = World()

        self.conversations = []

    # Setup {{{1
    def setup (self):
        pipes = self.server.get_pipes()

        # Create identities for the World.
        human_identities = range(len(pipes))
        #ai_identities = self.create_ai_identities()
        #player_identities = human_identities + ai_identities
        target_identities = range(game_settings.target_count)

        print 'Human identites: ', human_identities

        # Create the world.
        self.world.setup(human_identities, target_identities)
        #self.world.setup(player_identities, target_identities)

        # Prepare to send info to the clients.
        for identity in human_identities:
            pipe = pipes[identity]
            setup_world = SetupWorld(self.world, identity)
            self.conversations.append(SimpleSend(pipe, setup_world))

        # Start the conversations.
        for conversation in self.conversations:
            conversation.start()

    # Update, Callbacks, and Methods {{{1
    def update(self, time):
        active_conversations = []
        for conversation in self.conversations:
            if not conversation.finished():
                active_conversations.append(conversation)
                conversation.update()
        if active_conversations: self.conversations = active_conversations
        else: self.exit_engine()

    def successor (self):
        pipes = self.server.get_pipes()
        forum = Forum(*pipes, safe=False)

        return ServerGame(self.loop, forum, self.world)

    def teardown(self):
        pass
    # }}}1

class ServerGame (Engine):
    """ Sets up the game on the server then plays it. The server controls the 
    game logic and will send the results to clients. Eventually, the server 
    will run the AI too. """
    # Constructor {{{1
    def __init__ (self, loop, forum, world):
        print 'S: Begin game engine.'
        Engine.__init__ (self, loop)

        # Store the basic services.
        self.forum = forum
        self.world = world

        # Create the relays.
        publisher = self.forum.get_publisher()
        subscriber = self.forum.get_subscriber()

        self.referee = Referee(self, publisher, self.world)
        self.reflex = Reflex(self, subscriber, self.world)
        #ai_relay = AIRelay(self)

        #self.gui = server_gui.SimpleGui(self.world)

    def setup (self):
        self.referee.setup()
        self.reflex.setup()

        #self.gui.setup()

        self.forum.lock()

    # Update {{{1
    def update (self, time):
        self.forum.update()
        self.reflex.update(time)
        self.world.update(time)
        self.referee.update(time)

        #self.gui.update(time)

    # Methods {{{1
    def game_over(self):
        # Called by the Referee. 
        self.exit_loop()
        print 'S: Ending loop.'

    def successor(self):
        #return ServerPostgame(self.loop)
        return None
    
    def teardown(self):
        time.sleep(5)
        self.reflex.teardown()
        self.referee.teardown()
        self.forum.teardown()
        self.world.teardown()
        print "Server terminated."
# }}}1

class ServerPostgame (Engine):
    # Is not used. Exists just in case a use comes up.
    # Postgame {{{1
    def __init__ (self, loop):
        Engine.__init__ (self, loop)

    def setup (self):
        pass

    def update (self, time):
        self.exit_loop()

    def teardown (self):
        pass
# }}}1


class ClientNetworkSetup (Engine):
    # Sets up the network for the client.
    # Constructor {{{1
    def __init__ (self, loop):
        print 'C: Network setting up.'
        Engine.__init__ (self, loop)

        host = network_settings.host
        port = network_settings.port
        callback = self.connected
        self.client = PickleClient (host, port, callback)

    def setup (self):
        pass

    # Update, Callback, and Methods {{{1
    def update (self, time):
        self.client.connect()

    def connected(self, pipe):
        print 'C: Client connected.'
        self.exit_engine()

    def successor (self):
        return ClientPregame(self.loop, self.client)
    
    def teardown (self):
        pass
    # }}}1

class ClientPregame (Engine):
    # Constructor {{{1
    def __init__ (self, loop, client):
        print 'C: Begin pregame.'
        Engine.__init__(self, loop)
        self.client = client

        self.world = None
        self.conversation = None

    def setup(self):
        pipe = self.client.get_pipe()
        flavor = SetupWorld
        callback = self.setup_world
        self.conversation = SimpleReceive(pipe, flavor, callback)
        self.conversation.start()

    # Update, Callbacks, and Methods {{{1
    def update(self, time):
        if not self.conversation.finished(): self.conversation.update()
        else: self.exit_engine()

    def setup_world(self, message):
        self.world = message.world
        self.world.set_owner_identity(message.identity)

    def successor (self):
        pipe = self.client.get_pipe()
        forum = Forum(pipe, safe=False)

        return ClientGame(self.loop, forum, self.world)
    
    def teardown (self):
        pass
    # }}}1
        
class ClientGame (Engine):
    """ Plays the game. Does not have any game logic. It send player input to
    the server which will eventually tell the client's game what to do. """
    # Constructor {{{1
    def __init__ (self, loop, forum, world):
        print 'C: Begin game engine.'
        Engine.__init__ (self, loop)

        self.forum = forum
        self.world = world
        
        # Set up the relays.
        publisher = self.forum.get_publisher()
        subscriber = self.forum.get_subscriber()

        self.reflex = Reflex(self, subscriber, self.world)
        self.player_relay = PlayerRelay(self, publisher, self.world)

        self.gui = Gui(self.world, self.player_relay)

    def setup (self):
        self.reflex.setup()
        self.player_relay.setup()
        self.gui.setup()

        self.forum.lock()
    
    # Update {{{1
    def update (self, time):
        self.forum.update()
        self.reflex.update(time)
        self.player_relay.update(time)
        self.world.update(time)
        self.gui.update(time)

    # Methods {{{1
    def game_over(self):
        # Called by the Reflex?
        print 'Game over.'
        self.exit_engine()

    def successor (self):
        self.forum.unlock()
        return ClientPostgame(self.loop, self.forum, self.world, self.gui)
    
    def teardown (self):
        time.sleep(1)
    # }}}1

class ClientPostgame (Engine):
    """ The game does not close immediately, waits for player to close it. 
    Allows the victor time to feel good about themselves. Shows stats from the
    world frozen when the player quit. """
    # Postgame {{{1
    def __init__ (self, loop, forum, world, gui):
        Engine.__init__ (self, loop)
        self.forum = forum
        self.world = world
        self.gui = gui

    def setup (self):
        #self.forum.subscribe(Quit, self.quit)
        self.forum.lock()

    def update (self, tiempo):
        #self.forum.update()
        # self.gui.update (time)
        time.sleep(1)
        self.exit_loop()
        
    def quit (self, message):
        self.exit_loop()

    def teardown (self):
        time.sleep(5)
        self.gui.teardown()
        self.forum.teardown()
        self.world.teardown()
        print "Client terminated."
# }}}1
