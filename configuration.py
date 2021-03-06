__author__ = "amritansh"

import math
import random
import pygame
import pygame.color as color

import boid
import mapparser as mp
from prm import PRMGenerator


class Configuration:
    """
    Static class that holds important global variables
    """

    ## Dimensions of the screen
    dim = xSize, ySize = 1000, 600

    ## Number of sample points to use in the PRM
    numSamplePoints = 300

    ## Defines the radius of all goals
    goalRadius = 20

    ## Maximum speed of the boids
    boidSpeed = 30

    ## Number of neighbours the boids will influence
    ## a boid's heading
    numNeighbours = 3

    ## The screen used to draw the simluation
    screen = pygame.display.set_mode(dim)

    ## The list of colors (used for debugging purposes)
    colorList = map(
        lambda k: color.THECOLORS[k],
        color.THECOLORS.keys()
    )

    boid_radius = 4


class PolyFileConfiguration(Configuration):
    """
    Extends the Configuration class. This configuration gets the
    obstacles from .map files that have been created.
    """

    def parseDynamicObstacles(self, dynamic_obstacles_fp):
        """
        Parses the obstacle map file and creates polygon objects with random
        behaviour by default. All obstacles (static/dynamic) obtains a list
        each other in the form of a list.
        """
        # parse the obstacle file and create Polygons
        if dynamic_obstacles_fp is not None:
            dyn_obstacles = mp.mparse(dynamic_obstacles_fp, self.obstacleList)
            for obst in dyn_obstacles:
                self.obstacleList.append(obst)

            # pass a copy of obstacle list to each dynamic obstacle
            for obst in self.obstacleList:
                obst.obstacles = list(self.obstacleList)  # make cpy not ref
                if obst.dynamic:
                    obst.removeSelfFromObstacleList()

    def _autoGeneratedObstacleValid(self, node, nogo_zones):
        """
        Checks to see if the vertices are inside an obstacle already
        """
        # check against obstacles
        for obst in self.obstacleList:
            res = obst.pointInPoly(node)
            if res:
                return False  # node is invalid, it is inside an obstacle
            if obst.norm(node, obst.getPoint(node)) <= 20:
                return False

        # check if node is near nogo_zones
        for zone in nogo_zones:
            distance_between = math.sqrt(
                (zone[0] - node[0]) ** 2 + (zone[1] - node[1]) ** 2
            )

            if distance_between < 150:
                return False

        # check against other about-to-be obstacles (i.e. other nodes)
        # make sure they are no where near each other!
        for other_node_set in self.nodes[:-1]:
            for other_node in other_node_set:
                n_1 = list(node)
                n_2 = list(other_node)

                # pythagoras theorem
                x = n_1[0] - n_2[0]
                y = n_1[1] - n_2[1]
                dist = math.sqrt(math.pow(x, 2) + math.pow(y, 2))

                # should be bigger than 30 units away from each other
                if dist < 30:
                    return False

        return True

    def autoGenerateDynamicObstacles(self, start_point, end_point):
        """
        Auto generate dynamic obstacles
        """
        width = 30
        height = 30
        top_left = [0, 0]
        top_right = [0, 0]
        bottom_left = [0, 0]
        bottom_right = [0, 0]
        self.nodes = list()

        obst_generated = 0
        obst_validated = True

        nogo_zones = [start_point, end_point]

        while (obst_generated < self.auto_gen_number):
            # generate vertices at random co-ordinates for dynamic obstacles
            top_left[0] = random.randint(40, Configuration.xSize - 40)
            top_left[1] = random.randint(40, Configuration.ySize - 40)
            top_right = [top_left[0] + width, top_left[1]]
            bottom_right = [top_right[0], top_right[1] - height]
            bottom_left = [bottom_right[0] - width, bottom_right[1]]
            self.nodes += [[
                tuple(top_left),
                tuple(top_right),
                tuple(bottom_right),
                tuple(bottom_left)
            ]]

            # check to see if vertices lye in obstacles
            for node in self.nodes[-1]:
                if self._autoGeneratedObstacleValid(node, nogo_zones) is False:
                    obst_validated = False
                    self.nodes.pop()  # remove from nodes
                    break
                else:
                    obst_validated = True

            # if obstacle nodes are good, increment obstacles generated
            if obst_validated:
                obst_generated += 1

        # with the vertices generated create the dynamic obstacle objects
        dyn_obstacles = mp.mparse(
            None,
            self.obstacleList,
            nodes=self.nodes,
            start_point=start_point,
            end_point=end_point
        )
        for obst in dyn_obstacles:
            self.obstacleList.append(obst)

        # pass a copy of obstacle list to each dynamic obstacle
        for obst in self.obstacleList:
            obst.obstacles = list(self.obstacleList)  # make cpy not ref
            if obst.dynamic:
                obst.removeSelfFromObstacleList()

    def determinePositionInConfig(self, i, flockSize, startPoint):
        boid_radius = Configuration.boid_radius
        init_length = math.ceil(math.sqrt(flockSize))
        down = int(i // init_length)
        accross = int(i % init_length)

        return (
            startPoint[0] + 3 * boid_radius * accross,
            startPoint[1] + 3 * boid_radius * down
        )

    def initVars(
        self,
        startPoint,
        endPoint,
        flockSize,
        **kwargs
    ):
        """
        Parses the file to get the obstacle list. Creates a PRM generator to
        create a global map of the environment. Gets the list of intermediate
        goals.  Also, creates the list of boids used in the simulation
        @param startPoint The starting point for the boids
        @param endPoint The ending point for the boids
        @param flockSize The size of the flock (number of boids)
        @param filename The name of the file that contains the environment map
        """
        ## List of obstacles
        # parse static obstalces
        self.obstacleList = mp.mparse(kwargs.get("map_file", "maps/m1.map"))

        # parse dynamic obstalces
        dynamic_obstacles_fp = kwargs.get("dynamic_obstacles", None)
        self.parseDynamicObstacles(dynamic_obstacles_fp)

        # auto geneate dynamic obstacles
        self.auto_gen_obst = kwargs.get("auto_gen_obst", False)
        self.auto_gen_number = kwargs.get("auto_gen_number", 0)
        if self.auto_gen_obst:
            self.autoGenerateDynamicObstacles(startPoint, endPoint)

        ## Starting point
        self.startPoint = startPoint

        ## Ending point
        self.endPoint = endPoint

        ## Object containing variables and mehtods for the global planner
        self.prmGen = PRMGenerator(
            startPoint,
            endPoint,
            self.obstacleList,
            Configuration.xSize,
            Configuration.ySize,
            Configuration.numSamplePoints,
            Configuration.screen
        )

        ## List of intermediate goals derived by the global planner
        self.goalList = self.prmGen.generate(Configuration.goalRadius)

        ## List of boids in the flock
        self.boidList = [
            boid.Boid(
                startPoint,
                endPoint,
                Configuration.boidSpeed,
                Configuration.xSize,
                Configuration.ySize,
                Configuration.numNeighbours,
                boid.guassianFunc,
                self.obstacleList,
                self.goalList,
                self.prmGen,
                Configuration.screen,
                Configuration.colorList[i],
                Configuration.boid_radius,
                self.determinePositionInConfig(i, flockSize, startPoint)
            ) for i in range(flockSize)
        ]
