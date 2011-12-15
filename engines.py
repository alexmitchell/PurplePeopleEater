#used for debugging
import time
import sys
import random

import network_settings
import game_settings
from relays import *
from world import World

from utilities.core import Engine
from utilities.network import Server
from utilities.network import Client
from utilities.messaging import Forum


class ServerNetworkSetup (Engine):
    """ Gets the server ready to run the game: Sets up the network, connect to
    clients, set up the forum. """
    
    # Consructor {{{1
    def __init__ (self, loop):
        Engine.__init__ (self, loop)

        host = network_settings.host
        port = network_settings.port
        seats = network_settings.seats
        callback = self.server_full_callback
        self.server = Server (host, port, seats, callback)

    def setup (self):
        pass

    # Update {{{1
    def update (self, time):
        self.server.accept()

    # Methods {{{1
    def server_full_callback(self, *pipes):
        self.finish()

    def successor (self):
        return ServerPregame(self.loop, self.server)
    
    def teardown (self):
        pass
    # }}}1

class ServerPregame (Engine):
    """ Sets up the world and makes sure the clients receive it. Eventually 
    allow for users to modify the initial world settings plus personalizations
    like name or color. """
    # Constructor {{{1
    def __init__ (self, loop, server):
        Engine.__init__(self,loop)
        self.server = server

        pipes = server.get_pipes()
        self.forum = Forum(pipes)

        self.world = World()

    # Setup {{{1
    def setup (self):
        # Gather identities for the World.
        human_identities = self.get_player_identities()
        #ai_identities = self.get_ai_identities()
        #player_identities = human_identities + ai_identities
        target_identities = self.get_target_identities()

        self.world.setup(human_identities, target_identities)
        #self.world.setup(player_identities, target_identities)

        for eater_id in self.get_eaters(player_identities):
            self.world.change_eater(eater_id, infinity)

        # Set up any subscriptions for receiving info from the client. Lock 
        # when finished.
        self.forum.lock()

        # Send the world to everyone:
        world_message = WorldMessage(self.world)
        self.forum.publish(world_message, self.finish_pregame)

    def get_player_identities(self):
        pipes = self.server.get_pipes()
        identities = []
        for pipe in pipes:
            identities.append(pipe.get_remote_id())
        return identities
    
    def get_target_identities(self):
        identities = range(game_settings.target_count)
        return identities

    def get_eaters (self, players):
        count = game_settings.eater_count
        eaters = random.sample(players, count)
        return eaters

    # Update, Callbacks, and Methods {{{1
    def update(self, time):
        self.forum.update()

    def all_done (self, message):
        self.forum.publish(FinishPregame(), self.finish)

    def successor (self):
        self.forum.unlock()
        return ServerGame(self.loop, self.forum, self.world)

    def teardown(self):
        pass
    # }}}1

class ServerGame (Engine):
    """ Sets up the game on the server then plays it. The server controls the 
    game logic and will send the results to clients. Eventually, the server 
    will run the AI too. """
    # Constructor {{{1
    def __init__ (self, loop, forum, world):
        Engine.__init__ (self, loop)

        # Store the basic services.
        self.forum = forum
        self.world = world

        # Create the relays.
        self.referee = relays.Referee(self)
        self.reflex = relays.Reflex(self)
        #ai_relay = relays.AIRelay(self)

    def setup (self):
        self.referee.setup(self.forum, self.world)
        self.reflex.setup(self.forum, self.world)

        self.forum.lock()

    # Update {{{1
    def update (self, time):
        self.forum.update()
        self.reflex.update(time)
        self.world.update()
        self.referee.update(time)

    # Methods {{{1
    def successor (self):
        #return ServerPostgame(self.loop)
        return None
    
    def teardown (self):
        print 'Server game tearing down'
        self.relay.teardown()
        self.referee.teardown()
        self.forum.teardown()
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


class ClientNetworkSetup (Engine):
    # Sets up the network and forum for the client.
    # Constructor {{{1
    def __init__ (self, loop):
        Engine.__init__ (self, loop)

        host = network_settings.host
        port = network_settings.port
        callback = self.connected
        self.client = Client (host, port, callback)

    def setup (self):
        pass

    # Update, Callback, and Methods {{{1
    def update (self, time):
        self.client.connect()

    def connected(self, pipe):
        self.forum.setup (pipe)
        self.finish()

    def successor (self):
        return ClientPregame(self.loop, self.client)
    
    def teardown (self):
        pass
    # }}}1

class ClientPregame (Engine):
    # Constructor {{{1
    def __init__ (self, loop, client):
        Engine.__init__(self, loop)
        self.client = client

        self.forum = Forum(client.get_pipe())
        self.world = None

    def setup(self):
        self.forum.subscribe(InitialWorld, self.initial_world)
        self.forum.subscribe(FinishPregame, self.finish_callback)
        
        self.forum.lock()

    # Update, Callbacks, and Methods {{{1
    def update(self):
        self.forum.update()

    def initial_world(self, message):
        self.world = message.world
        owner = self.client.get_pipe().get_local_id()
        self.world.set_owner(owner)

    def finish_callback(self, message):
        self.finish()

    def successor (self):
        self.forum.unlock()
        return ClientGame(self.loop, self.forum, self.world)
    
    def teardown (self):
        pass
    # }}}1
        
class ClientGame (Engine):
    """ Plays the game. Does not have any game logic. It send player input to
    the server which will eventually tell the client's game what to do. """
    # Constructor {{{1
    def __init__ (self, loop, forum, world):
        Engine.__init__ (self, loop)

        self.forum = forum
        self.world = world
        
        #self.gui = Gui(self)

        self.reflex = relays.Reflex(self)
        self.player_relay = relays.PlayerRelay(self)

        self.tasks = self.reflex, self.player_relay
        #self.tasks = self.reflex, self.gui, self.player_relay

    def setup (self):
        for task in self.tasks:
            task.setup(self.forum, self.world)
        self.forum.lock()
    
    # Update {{{1
    def update (self, time):
        self.forum.update()
        for task in self.tasks:
            task.update(time)

    # Methods {{{1
    def successor (self):
        self.forum.unlock()
        return ClientPostgame(self.loop, self.forum, self.world, self.gui):
    
    def teardown (self):
        print 'Client game tearing down'
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
        self.forum.subscribe(Quit(), self.quit)
        self.forum.lock()

    def update (self, time):
        self.forum.update()
        # self.gui.update (time)
        
    def quit (self, message):
        self.finish()

    def teardown (self):
        self.gui.teardown()
        self.forum.teardown()
        self.world.teardown()
        time.sleep(1)
# }}}1
