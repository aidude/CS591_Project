

__author__ = "amritansh"

import pygame

class CircleGoal:
    """
    Object that holds data about a goal modelled as
    circular configuration space
    """
    def __init__(self, _radius, _position, _screen):
    	"""
    	Creates an instance of the CircleGoal
    	@param _radius The radius of the circle goal
    	@param _position The position of the circle goal
    	@param _screen The pygame screen used to draw the circle
    	"""

    	## PyGame screen used to draw the circle goal
    	self.screen   = _screen

    	## List of colors given by PyGame
        self.colors   = pygame.color.THECOLORS

        ## The radius of the circle goal
        self.radius   = _radius

        ## The position of the circle goal
        self.position = _position

    def draw(self):
    	"""
    	Draws the circle onto the pygame screen
    	"""
        pygame.draw.circle(
            self.screen,
            self.colors["green"],
            self.position,
            self.radius,
            5
        )
