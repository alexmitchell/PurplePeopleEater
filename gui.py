import sys, math

import game_settings
import player_settings
import controls

import pygame
from pygame.locals import *

from shapes import *
from vector import *

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
        self.draw()

    def teardown(self):
        pass

    # Draw {{{1
    def draw(self):
        world = self.world
        screen = self.screen
        owner = world.get_owner_identity()

        # Draw the background. {{{2
        screen.fill(player_settings.background_color)

        # Draw the players. {{{2
        players = world.get_players()
        player_colors = player_settings.player_colors
        for identity, player in players:
            color = player_colors[identity]
            if identity in world.get_eater_identities():
                color = player_settings.eater_color

            position = player.get_position().pygame
            radius = player.get_radius()

            pygame.draw.circle(screen, color, position, radius)

        # Draw the targets. {{{2
        targets = world.get_targets()
        target_color = player_settings.target_color
        is_eater = owner in world.get_eater_identities()
        for target in targets:
            position = target.get_position().get_pygame()
            radius = target.get_radius()

            if is_eater:
                pygame.draw.circle(screen, target_color, position, radius)
            else:
                progress = 1 - button.get_timer() / button.get_timeout()
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
        template = "%s: %d HP"
        status = template % (player_settings.owner_name, owner.get_life())

        #map_size = self.size
        #width, height = self.status_font.size(your_status)

        my_position = 5, 5
        #your_position = map_size.x - width - 5, 5

        text color = player_settings.text_color
        my_message = self.status_font.render(my_status, True, text_color)
        #your_message = self.status_font.render(your_status, True, settings.text_color)

        screen.blit(my_message, my_position)
        #screen.blit(your_message, your_position)
        # }}}2

        # Finish the update. 
        pygame.display.flip()

    # }}}1
    # Attributes {{{1
    def get_world(self):
        return self.world

    #}}}1

