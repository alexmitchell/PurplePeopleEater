from utilities.core import Loop

import engines

class ServerLoop (Loop):
    def __init__ (self):
        self.engine = engines.ServerPregame(self)

class UserLoop (Loop):
    def __init__ (self):
        self.engine = engines.ClientPregame(self)

if __name__ == "__main__":
    pass
    # sys.argv[1] for server, client option?