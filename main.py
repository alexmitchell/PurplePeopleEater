from kxgames.core import Loop

import engines

class ServerLoop (Loop):
    def __init__ (self):
        self.engine = engines.ServerNetworkSetup(self)

class UserLoop (Loop):
    def __init__ (self):
        self.engine = engines.ClientNetworkSetup(self)
