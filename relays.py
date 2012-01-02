import random

import game_settings
from messages import *
from kxgames.vector import Vector
from kxgames.messaging import Forum
from kxgames.core import Task

class Reflex (Task):
    """ The only relay that can change the world (data)."""
    # Constructor {{{1
    def __init__ (self, engine, forum, world):
        Task.__init__ (self, engine)

        self.forum = forum 
        self.world = world

    def setup (self):
        forum = self.forum
        # set up subscriptions
        forum.subscribe(Sync, self.sync)
        forum.subscribe(Accelerate, self.accelerate)
        forum.subscribe(Bite, self.bite)
        forum.subscribe(ChangeEater, self.change_eater)
        forum.subscribe(DestroyPlayer, self.destroy_player)
        forum.subscribe(MoveTarget, self.move_target)
        forum.subscribe(Bounce, self.bounce)
        forum.subscribe(GameOver, self.game_over)
    # }}}1

    # Sync {{{1
    def sync (self, message):
        positions = message.positions_dict
        velocities = message.velocities_dict
        #accelerations = message.accelerations_dict
        players = self.world.players

        for identity, player in players.items():
            player.set_position(positions[identity])
            player.set_velocity(velocities[identity])

            #behavior = player.get_player_behavior()
            #behavior.set_acceleration(accelerations[identity])

    # Accelerate {{{1
    def accelerate (self, message):
        try:
            identity = message.identity
            ratio = message.acceleration_ratio

            player = self.world.players[identity]
            max_a = player.get_max_acceleration()
            behavior = player.get_player_behavior()

            acceleration = ratio * max_a
            behavior.set_acceleration(acceleration)
        except KeyError:
            pass

    # Bite {{{1
    def bite (self, message):
        biter_identity = message.biter
        eaters = self.world.eater_identities
        if biter_identity in eaters:
            players = self.world.players
            for player in players.keys():
                if not player == biter_identity and player not in eaters:
                    attacker = players[biter_identity]
                    victim = players[player]
                    if self.token_collision(attacker, victim):
                        damage = attacker.get_bite_damage()
                        victim.damage(damage, biter_identity)
        else:
            targets = self.world.targets
            for target in targets.values():
                try:
                    human = self.world.players[biter_identity]
                    if self.token_collision(human, target):
                        damage = human.get_bite_damage()
                        target.damage(damage, biter_identity)
                except KeyError:
                    pass

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


    # Bounce {{{1
    def bounce(self, message):
        identity = message.identity
        orientations = message.orientations
        player = self.world.players[identity]
        radius = game_settings.player_radius

        x, y = player.get_position().get_pygame()
        vx, vy = player.get_velocity().get_pygame()
        map_x, map_y = self.world.get_map_size().get_pygame()
        old_vx = vx
        old_vy = vy

        for orientation in orientations:
            if 'Left' == orientation:
                x = radius
                vx *= -1
            elif 'Right' == orientation:
                x = map_x - radius
                vx *= -1
            if 'Top' == orientation:
                y = map_y - radius
                vy *= -1
            elif 'Bottom' == orientation:
                y = radius
                vy *= -1

        owner_id = self.world.get_owner_identity()
        player.set_position(Vector(x,y))
        player.set_velocity(Vector(vx,vy))

    # GameOver {{{1
    def game_over(self, message):
        winner = message.winner
        self.world.winner = winner
        self.engine.game_over()
        if winner == self.world.owner_identity: print 'You won!'
        else: print 'You lost.'
    # }}}1

    # Update and methods {{{1
    def update (self, time):
        pass

    def token_collision(self, token_1, token_2):
        position_1 = token_1.get_position()
        position_2 = token_2.get_position()
        difference = position_2 - position_1
        distance = difference.get_magnitude_squared()

        r1 = token_1.get_radius()
        r2 = token_2.get_radius()
        critical = (r1 + r2)**2

        return distance <= critical

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

        self.sync_frequency = game_settings.sync_frequency
        self.sync_timer = 0

    def setup (self):
        pass

    # Update {{{1
    def update (self, time):
        forum = self.forum
        players = self.world.get_players()
        targets = self.world.get_targets()

        # Periodically send Sync message {{{2
        self.sync_timer += time
        if self.sync_timer >= self.sync_frequency:
            self.sync_timer -= self.sync_frequency
            sync_positions = {}
            sync_velocities = {}
            sync_accelerations = {}

            for identity, player in self.world.players.items():
                sync_positions[identity] = player.get_position()
                sync_velocities[identity] = player.get_velocity()
                sync_accelerations[identity] = player.get_acceleration()

            sync = Sync(sync_positions, sync_velocities, sync_accelerations)
            forum.publish(sync)

        # }}}2

        # Check for number of players. If only one, announce winner. {{{2
        if 1 == len(players):
            winner_list = players.values()
            winner = winner_list[0].get_identity()
            game_over = GameOver(winner)
            forum.publish(game_over)
        # }}}2

        for identity, player in players.items():
            # Check player life. Destroy player if life 0. {{{2
            if player.get_life() <= 0:
                destroy_player = DestroyPlayer(identity)
                forum.publish(destroy_player)
            # Check for a bounce {{{2
            orientations = self.check_bounce(player)
            if len(orientations) > 0:
                bounce = Bounce(identity, orientations)
                forum.publish(bounce)
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
    def check_bounce(self, player):
        radius = game_settings.player_radius
        map_x, map_y = self.world.get_map_size().get_pygame()
        x,y = player.get_position().get_pygame()
        orientations = []

        if x < radius: orientations.append('Left')
        elif x > (map_x - radius): orientations.append('Right')

        if y < radius: orientations.append('Bottom')
        elif y > (map_y - radius): orientations.append('Top')

        return orientations
        
    def random_position(self):
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

    # Accelerate {{{1
    def accelerate(self, acceleration_ratio):
        ratio = Accelerate(self.world.get_owner_identity(), acceleration_ratio)
        self.forum.publish(ratio)

    # Bite {{{1
    def bite(self):
        bite = Bite(self.world.get_owner_identity())
        self.forum.publish(bite)

    # Quit {{{1
    def quit(self):
        destroy = DestroyPlayer(self.world.get_owner_identity())
        self.forum.publish(destroy)

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
