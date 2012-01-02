import sys, math

import game_settings
import player_settings
import controls

import pygame
from pygame.locals import *

from kxgames.vector import Vector

class Gui:
    # Constructor {{{1
    def __init__ (self, world, relay):
        self.world = world
        self.relay = relay

        self.size = game_settings.map_size

        self.input = None
        self.controls = {
                "joystick" : controls.Joystick(self),
                "keyboard" : controls.Keyboard(self),
                "experimental" : controls.Experimental(self) }

    def setup(self):
        pygame.init()

        # Create a window to run the game in.
        self.screen = pygame.display.set_mode(self.size.get_pygame())

        self.status_font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 50)

        # Set up the user controls.
        self.input = self.controls[player_settings.controller_type]
        self.input.setup()

        self.input.on_motion(self.relay.accelerate)
        self.input.on_button(self.relay.bite)

    # Update {{{1
    def update(self, time):
        self.input.update()
        self.draw(time)

    def teardown(self):
        pass

    # Draw {{{1
    def draw(self, time):
        screen = self.screen
        world = self.world
        players = world.get_players()
        targets = world.get_targets()
        owner_identity = world.get_owner_identity()

        # Draw the background. {{{2
        #screen.fill(player_settings.background_color)

        # Draw the players. {{{2
        player_colors = player_settings.player_colors
        for identity, player in players.items():
            color = player_colors[identity]
            if identity in world.get_eater_identities():
                color = player_settings.eater_color

            position = player.get_position().pygame
            radius = player.get_radius()

            self.erase_sprite(player, time)
            pygame.draw.circle(screen, color, position, radius)

        # Draw the targets. {{{2
        target_color = player_settings.target_color
        is_eater = owner_identity in world.get_eater_identities()
        for target in targets.values():
            position = target.get_position().get_pygame()
            radius = target.get_radius()

            if is_eater:
                self.erase(target, time)
                pygame.draw.circle(screen, target_color, position, radius)
            else:
                progress = 1 - target.get_timer() / target.get_timeout()
                points = [position]

                for index in range(50):
                    fraction = index / 50
                    angle = 2 * math.pi * fraction

                    if fraction > progress:
                        break

                    x = position[0] + radius * math.cos(angle)
                    y = position[1] + radius * math.sin(angle)

                    point = x, y
                    points.append(point)

                if len(points) > 2:
                    pygame.draw.polygon(screen, color, points)

        # Draw a status message. {{{2
        try:
            template = "%s: %d HP"
            owner = players[owner_identity]
            status = template % (player_settings.owner_name, owner.get_life())

            text_position = 5, 5

            text_color = player_settings.text_color
            text = self.status_font.render(status, True, text_color)

            screen.blit(text, text_position)
        except KeyError:
            pass
        # }}}2

        # Finish the update. 
        pygame.display.flip()

    # }}}1
    def erase_sprite(self, sprite, time):
        #color = player_settings.background_color
        color = Color("Red")
        position = sprite.get_position()
        velocity = sprite.get_velocity()
        radius = sprite.get_radius()

        offset = velocity * time
        center = (position - velocity).get_pygame()
        
        radius += 2

        pygame.draw.circle(self.screen, color, center, radius)


    # Attributes {{{1
    def get_world(self):
        return self.world

    #}}}1


