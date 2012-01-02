from __future__ import division
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

        self.erasers = []

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

        # Erase previous objects.
        for eraser in self.erasers:
            eraser.draw(screen)
        self.erasers = []

        # Draw the background.
        #screen.fill(player_settings.background_color)

        self.draw_targets(screen)
        self.draw_players(screen)
        self.draw_status_message(screen)

        # Finish the update. 
        pygame.display.flip()

    # Draw the targets. {{{2
    def draw_targets(self, screen):
        targets = self.world.get_targets()
        owner_identity = self.world.get_owner_identity()
        is_eater = owner_identity in self.world.get_eater_identities()

        target_color = player_settings.target_color
        background_color = player_settings.background_color

        for target in targets.values():
            position = target.get_position().get_pygame()
            radius = target.get_radius()

            self.erasers.append(CircleEraser(position, radius))

            if is_eater:
                pygame.draw.circle(screen, target_color, position, radius)
            else:
                progress = 1 - target.get_timer() / target.get_timeout()
                points = [position]

                # Draw the ring. Note drawing a thick circle won't work.
                ring = radius - player_settings.target_ring_thickness
                pygame.draw.circle(screen, target_color, position, radius)
                pygame.draw.circle(screen, background_color, position, ring)

                radius -= 1
                num = 100
                for index in range(num):
                    fraction = index / num
                    angle = 2 * math.pi * fraction

                    if fraction > progress:
                        break

                    x = position[0] + radius * math.cos(angle)
                    y = position[1] + radius * math.sin(angle)

                    point = x, y
                    points.append(point)

                if len(points) > 2:
                    pygame.draw.polygon(screen, target_color, points)


    # Draw the players. {{{2
    def draw_players(self, screen):
        players = self.world.get_players()
        player_colors = player_settings.player_colors
        for identity, player in players.items():
            position = player.get_position().pygame
            radius = player.get_radius()
            color = player_colors[identity]
            if identity in self.world.get_eater_identities():
                color = player_settings.eater_color
            
            self.erasers.append(CircleEraser(position, radius))

            pygame.draw.circle(screen, color, position, radius)

    # Draw a status message. {{{2
    def draw_status_message(self, screen):
        try:
            players = self.world.get_players()
            owner_identity = self.world.get_owner_identity()
            owner = players[owner_identity]

            template = "%s: %d HP"
            status = template % (player_settings.owner_name, owner.get_life())

            text_position = 5, 5

            text_color = player_settings.text_color
            text = self.status_font.render(status, True, text_color)

            dimensions = text.get_size()
            self.erasers.append(SquareEraser(text_position, dimensions))

            screen.blit(text, text_position)
        except KeyError:
            pass
        # }}}2
    # }}}1
    # Attributes {{{1
    def get_world(self):
        return self.world

    #}}}1

class Eraser:
    def __init__(self):
        raise NotImplementedError

    def draw(self):
        raise NotImplementedError

class CircleEraser (Eraser):
    def __init__ (self, center, radius):
        self.center = center
        self.radius = radius
        self.color = player_settings.background_color
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.center, self.radius)

class SquareEraser (Eraser):
    def __init__ (self, position, dimensions):
        self.rect = pygame.Rect(position, dimensions)
        self.color = player_settings.background_color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
