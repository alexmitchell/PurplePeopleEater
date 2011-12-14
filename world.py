from utilities.vector import Vector
import game_settings

class World:
    def __init__(self):
        self.players = {}
        self.target = None

class Widget:
    # Provides basic functionality for in game objects.
    def __init__ (self):
        self.location = Vector.null()
        self.veloctiy = Vector.null()
    
    def __setup__ (self):
        raise NotImplementedError

class Player (Widget):
    # Provides specialized functionality for players.
    def __init__ (self):
        Widget.__init__(self)
        #self.name = '' <<Server vs client?? How would they get the name?
        self.eater = False

class Target (Widget):
    def __init__ (self):
        Widget.__init__(self)
        self.timeout = 0
        self.timer = 0

    def setup (self):
        self.timeout = game_settings.timeout
        self.timer = game_settings.timeout
