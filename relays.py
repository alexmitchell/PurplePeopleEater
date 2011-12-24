import random

from utilities.messaging import Forum
from utilities.core import Task

class Reflex (Task):
    """ The only relay that can change the world (data)."""
    # Constructor {{{1
    def __init__ (self, engine, forum, world):
        Task.__init__ (self, engine)

        self.forum = forum 
        self.world = world

    def setup (self):
        # set up subscriptions
        forum.subscribe(Bite, self.bite)
        forum.subscribe(ChangeEater, self.change_eater)
        forum.subscribe(DestroyPlayer, self.destroy_player)
        forum.subscribe(MoveTarget, self.move_target)
        forum.subscribe(GameOver, self.game_over)
    # }}}1

    # Bite {{{1
    def bite (self, message):
        biter_identity = message.biter
        eaters = self.world.eater_identities
        if biter_identity in eaters:
            players = self.world.players
            for player in players.keys():
                if not player == biter_identity and player not in eater:
                    attacker = players[biter_identity]
                    victim = players[player]
                    if self.token_collision(attacker, victim):
                        damage = attacker.get_bite_damage()
                        victim.damage(damage, biter_identity)
        else:
            targets = self.world.targets
            for target in target.value():
                human = self.world.players[biter_identity]
                if self.token_collision(human, target):
                    damage = human.get_bite_damage()
                    target.damage(damage, biter_identity)

    # DestroyPlayer {{{1
    def destroy_player (self, message):
        self.world.destroy_player(message.identity)

    # ChangeEater {{{1
    def change_eater(self, message):
        self.world.change_eater(message.new, message.old)

    # MoveTarget {{{1
    def move_target(self, message):
        target = self.world.targets[message.identity]
        target.set_position(message.position)
        target.reset_timer()
        if message.reset_life:
            target.reset_life()

    # GameOver {{{1
    def game_over(self, message):
        self.world.winner = message.winner
        self.engine.finish()
    # }}}1

    # Update and methods {{{1
    def update (self, time):
        pass

    def token_collision(self, token_1, token_2)
        position_1 = token_1.get_position()
        position_2 = token_2.get_position()
        difference = position_2 - position_1
        distance = difference.get_magnitude_squared()

        r1 = token_1.get_radius()
        r2 = token_2.get_radius()
        critical = (r1 + r2)**2

        return distance <= critical:

    def teardown (self):
        pass
    # }}}1

class Referee (Task):
    """ Watches game data. When necessary, sends info to server (through
    forum). Note: Does not change game data! """
    # Constructor {{{1
    def __init__ (self, engine, forum, world):
        Task.__init__ (self, engine)

        self.forum = forum 
        self.world = world

    def setup (self):
        pass

    # Update {{{1
    def update (self, time):
        forum = self.forum
        players = self.world.get_players()
        targets = self.world.get_targets()

        # Check for number of players. If only one, announce winner. {{{2
        if 1 == len(players):
            winner = players[0].get_identity())
            game_over = GameOver(winner)
            forum.publish(game_over)
        # }}}2

        for identity, player in players.items():
            # Check player life. Destroy player if life below 0. {{{2
            if player.get_life() <= 0:
                destroy_player = DestroyPlayer(identity)
                forum.publish(destroy_player)
            # }}}2
        
        for identity, target in targets.items():
            # Check target life. Change eaters if life below 0. {{{2
            if target.get_life() <= 0:
                new_eater_id = target.get_last_attacker()
                eater_identities = self.world.get_eater_identities()
                old_eater_id= random.choice(eater_identities)
                change_eater = ChangeEater(new_eater_id, old_eater_id)

                new_position = self.random_position()
                move_target = MoveTarget(identity, new_position, reset=True)

                forum.publish(change_eater)
                forum.publish(move_target)

            # Check for timeouts. Move target if it has timed out. {{{2
            if target.get_timer() >= target.get_timeout():
                new_position = self.random_position()
                move_target = MoveTarget(identity, new_position)
                forum.publish(move_target)
            # }}}2

    # Methods {{{1
    def random_position(self)
        size = self.world.get_map_size()
        x = size.x * random.random()
        y = size.y * random.random()
        return Vector(x,y)

    def teardown (self):
        pass
    # }}}1

class PlayerRelay (Task):
    """ Listens to player input. Sends info to server (through forum).
    Note: Does not change game data! """
    # Constructor {{{1
    def __init__ (self, engine, forum, world):
        Task.__init__(self, engine)
        self.forum = forum
        self.world = world

    def setup (self):
        pass

    def accelerate(self, 
    def bite(self,
    # Update and methods {{{1
    def update (self, time):
        pass

    def teardown (self):
        pass
    # }}}1

""" class AIRelay (Task):
        Listens to AI commands, sends info to the server (through forum).
        Note: ai runs only on the server.
        Note: Does not change game data! """
