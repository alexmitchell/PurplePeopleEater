
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
