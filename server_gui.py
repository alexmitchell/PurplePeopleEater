import sys, math

import game_settings
import player_settings

import pygame
from pygame.locals import *

from kxgames.vector import Vector

class SimpleGui:
    # Constructor {{{1
    def __init__ (self, world):
        self.world = world

        self.size = game_settings.map_size

    def setup(self):
        pygame.init()

        # Create a window to run the game in.
        self.screen = pygame.display.set_mode(self.size.get_pygame())

        self.status_font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 50)

    # Update {{{1
    def update(self, time):
        self.draw()

    def teardown(self):
        pass

    # Draw {{{1
    def draw(self):
        screen = self.screen
        world = self.world
        players = world.get_players()
        targets = world.get_targets()

        # Draw the background. {{{2
        screen.fill(player_settings.background_color)

        # Draw the players. {{{2
        player_colors = player_settings.player_colors
        for identity, player in players.items():
            color = player_colors[identity]
            if identity in world.get_eater_identities():
                color = player_settings.eater_color

            position = player.get_position().pygame
            radius = player.get_radius()

            pygame.draw.circle(screen, color, position, radius)

        # Draw the targets. {{{2
        target_color = player_settings.target_color
        for target in targets.values():
            position = target.get_position().get_pygame()
            radius = target.get_radius()

            pygame.draw.circle(screen, target_color, position, radius)

        # Finish the update. 
        pygame.display.flip()

    # }}}1
    # Attributes {{{1
    def get_world(self):
        return self.world

    #}}}1
