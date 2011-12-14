from utilities.vector import Vector
import game_settings

class World:
    def __init__ (self):
        self.owner = None

        self.players = {}
        self.target = Widget()

        self.eater = None
        self.timeout = game_settings.timeout
        self.timer =  0

    def setup (self, player_count):
        # Create the correct number of player objects.
        for i in range(player_count):
            player = Widget()
            player.setup()
            self.players.append(player)

        self.target.setup()

    def set_player_ids (self, id_dictionary):
        """ This function should only be called by the server and only once.
        This should ensure that each player will have a unique id and will be
        consistent on all instances of the game over the network. After the 
        id's are assigned on the server, they will be spread across the 
        network."""
        for i in range(len(id_dictionary)):
            player = self.players[i]
            id = id_dictionary[i]
            player.set_id (id)


class Widget:
    """  Provides basic functionality for in game objects. Each widget can 
    have an id. It is stored as an entry in a dictionary. 
    Example:  1234 : 'Player 1'  """
    def __init__ (self):
        self.id = {}
        # example:  1234 : 'Player 1'
        self.location = Vector.null()
        self.veloctiy = Vector.null()
    
    def setup (self):
        pass

    def set_id (self, id_dictionary):
        self.id = id_dictionary
