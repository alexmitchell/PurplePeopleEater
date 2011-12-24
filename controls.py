import sys

import pygame
from pygame.locals import *

from vector import *

class Controller:
    """ Base class for the two control methods.  Mostly responsible for
    registering callbacks. """

    # Setup {{{1
    def __init__(self, gui):
        """ Set up some basic class attributes.  Not too much can be done in
        the constructor, since it is called from the settings scripts. """

        self.gui = gui
        self.callbacks = {
                "motion" : lambda direction: None,
                "button" : lambda: None }

    def setup(self):
        """ Perform any additional setup that needs to be done.  This method is
        called after the rest of the game is setup, so anything goes. """
        raise NotImplementedError

    def update(self):
        """ Poll for input events and invoke the proper handler. """
        raise NotImplementedError

    # Callbacks {{{1
    def on_button(self, callback):
        """ Register a callback for a button event. """
        self.callbacks["button"] = callback

    def on_motion(self, callback):
        """ Register a callback for a motion event. """
        self.callbacks["motion"] = callback
    # }}}1

class Joystick(Controller):
    """ Control the game using a joystick.  This is the preferred mode of user
    input; the mouse-pad controller is really just meant to emulate this. """

    # Constructor {{{1
    def __init__(self, gui):
        Controller.__init__(self, gui)

        self.x = self.y = 0
        self.joystick = None

        self.handlers = {
                QUIT : self.quit_event,
                JOYAXISMOTION : self.motion_event,
                JOYBUTTONDOWN : self.button_event }

    # Update {{{1
    def setup(self):
        """ Connect to the joystick and prepare to begin accepting input.  If
        no joystick is found, the game will exit with an error message. """

        pygame.joystick.init()

        if not pygame.joystick.get_count():
            print "No joystick found."
            print "Consider using the keyboard controller."
            sys.exit()

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

    def update(self):
        """ Check to see if any joystick events have occurred since the last
        update cycle.  If so, perform any necessary processing and execute the
        appropriate callback. """

        for event in pygame.event.get():
            try:
                self.handlers[event.type](event)
            except KeyError:
                pass

    # Event Handlers {{{1
    def motion_event(self, event):
        """ This is an internal handler to joystick motion events.  Only motion
        along the x and y coordinates is acted upon. """

        X, Y, Z = 0, 1, 2

        if event.axis in (X, Y):
            if event.axis == X: self.x = event.value
            if event.axis == Y: self.y = event.value

            direction = Vector(self.x, self.y)
            self.callbacks["motion"](direction)

        elif event.axis == Z:
            pass

        else:
            raise AssertionError

    def button_event(self, event):
        """ This is an internal handler for joystick button events.  No
        processing is done; the callback is just executed immediately. """
        self.callbacks["button"]()

    def quit_event(self, event):
        """ This is an internal handler for any quit events.  This works by
        simply instructing the world to send a game over message. """
        world = self.gui.get_world()
        world.game_over()
    # }}}1

class Keyboard(Controller):
    """ Control the game using the keyboard.  For optimal gameplay, this
    controller should not be used.  It is instead supposed to be a joystick
    replacement for debugging purposes. """

    # Constructor {{{1
    def __init__(self, gui):
        Controller.__init__(self, gui)

        self.direction = Vector.null()
        self.controls = {
                K_RETURN : self.button_event,
                K_UP     : lambda type: self.motion_event(type,  0, -1),
                K_DOWN   : lambda type: self.motion_event(type,  0,  1),
                K_LEFT   : lambda type: self.motion_event(type, -1,  0),
                K_RIGHT  : lambda type: self.motion_event(type,  1,  0) }

    # Update {{{1
    def setup(self):
        """ No setup needs to be done. """
        pass

    def update(self):
        """ Poll for and handle keyboard events as they occur. """
        for event in pygame.event.get():
            try:
                self.controls[event.key](event)

            except AttributeError: pass     # Not a keyboard event.
            except KeyError: pass           # Not a known key.

    # Event Handlers {{{1
    def button_event(self, event):
        """ This is an internal handler for button events.  The callback is
        only called when the return key is released. """
        if event.type == KEYUP:
            self.callbacks["button"]()

    def motion_event(self, event, x, y):
        """ This is an internal handler for arrow key events.  The controls are
        not very fine; each direction is either on or off. """

        if event.type == KEYDOWN:
            self.direction += Vector(x, y)
        if event.type == KEYUP:
            self.direction -= Vector(x, y)

        self.callbacks["motion"](self.direction)
    # }}}1

class Experimental(Controller):
    """ An unconventional user interface that uses every key on the keyboard.
    The further away a key is from the center of the keyboard, the more
    influence it has. """

    # Constructor {{{1
    def __init__(self, gui):
        Controller.__init__(self, gui)

        self.keys = []
        self.center = K_k

        # Locations {{{2
        self.locations = {
                # First Row:
                K_BACKQUOTE         : Vector(-13.0, -2.78),
                K_1                 : Vector(-11.1, -2.78),
                K_2                 : Vector( -9.2, -2.78),
                K_3                 : Vector( -7.2, -2.78),
                K_4                 : Vector( -5.3, -2.78),
                K_5                 : Vector( -3.4, -2.78),
                K_6                 : Vector( -1.5, -2.78),
                K_7                 : Vector(  0.5, -2.78),
                K_8                 : Vector(  2.4, -2.78),
                K_9                 : Vector(  4.3, -2.78),
                K_0                 : Vector(  6.2, -2.78),
                K_MINUS             : Vector(  8.1, -2.78),
                K_PLUS              : Vector( 10.1, -2.78),
                K_BACKSPACE         : Vector( 13.0, -2.78),
                                             
                # Second Row:                
                K_TAB               : Vector(-12.5, -0.98),
                K_q                 : Vector(-10.1, -0.98),
                K_w                 : Vector( -8.2, -0.98),
                K_e                 : Vector( -6.3, -0.98),
                K_r                 : Vector( -4.4, -0.98),
                K_t                 : Vector( -2.5, -0.98),
                K_y                 : Vector( -0.5, -0.98),
                K_u                 : Vector(  1.4, -0.98),
                K_i                 : Vector(  3.3, -0.98),
                K_o                 : Vector(  5.2, -0.98),
                K_p                 : Vector(  7.1, -0.98),
                K_LEFTBRACKET       : Vector(  9.0, -0.98),
                K_RIGHTBRACKET      : Vector( 10.9, -0.98),
                K_BACKSLASH         : Vector( 13.4, -0.98),
                                             
                # Third Row:                 
                K_CAPSLOCK          : Vector(-12.3,  0.93),
                K_a                 : Vector( -9.6,  0.93),
                K_s                 : Vector( -7.7,  0.93),
                K_d                 : Vector( -5.8,  0.93),
                K_f                 : Vector( -3.9,  0.93),
                K_g                 : Vector( -2.0,  0.93),
                K_h                 : Vector( -0.0,  0.93),
                K_j                 : Vector(  1.9,  0.93),
                K_k                 : Vector(  3.8,  0.93),
                K_l                 : Vector(  5.7,  0.93),
                K_SEMICOLON         : Vector(  7.6,  0.93),
                K_QUOTE             : Vector(  9.5,  0.93),
                K_RETURN            : Vector( 12.8,  0.93),
                                             
                # Fourth Row:                
                K_LSHIFT            : Vector(-11.8,  2.83),
                K_z                 : Vector( -8.6,  2.83),
                K_x                 : Vector( -6.7,  2.83),
                K_c                 : Vector( -4.8,  2.83),
                K_v                 : Vector( -2.9,  2.83),
                K_b                 : Vector( -1.0,  2.83),
                K_n                 : Vector(  0.9,  2.83),
                K_m                 : Vector(  2.9,  2.83),
                K_COMMA             : Vector(  4.8,  2.83),
                K_PERIOD            : Vector(  6.7,  2.83),
                K_SLASH             : Vector(  8.6,  2.83),
                K_RSHIFT            : Vector( 12.3,  2.83) }
        # }}}2

    # Update {{{1
    def setup(self):
        key = pygame.key.name(self.center)
        print "Press any key near %s to move." % key

    def update(self):
        for event in pygame.event.get():
            if event.type not in (KEYUP, KEYDOWN):
                continue

            if event.key == K_SPACE:
                if event.type == KEYDOWN: self.callbacks["button"]()
                continue

            if event.type == KEYDOWN:
                self.keys.append(event.key)
            if event.type == KEYUP:
                self.keys.remove(event.key)

            center = self.locations[self.center]
            offset = Vector.null(); instructions = 0

            for key in self.keys:
                try:
                    offset += self.locations[key]
                    instructions += 1

                except KeyError:
                    pass

            try:
                offset = offset / instructions
                direction = offset - center

            except ZeroDivisionError:
                direction = Vector.null()

            self.callbacks["motion"](direction)
    # }}}1
