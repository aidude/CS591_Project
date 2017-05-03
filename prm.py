
__author__ = "amritansh"
import random
import dijkstra
import goal
import math as np
import pygame


class PRMGenerator:
    """
    Class used to hold methods and variables that are important
    for the global path planning problem. This class generates
    the roadmap and finds the shortest path to the the goals by
    determining intermediate goals for the boids to be attracted to
    """
    def __init__(
        self,
        _startPos,
        _endPos,
        _obstacleList,
        _xSize,
        _ySize,
        _subGoalNumber,
        _screen
    ):
        """
        Creates a new instance of the PRMGenerator. Intializes key variables
        used in the generation of the global planner.
        @param _startPos The starting position of the boids
        @param _endPos The final goal position of the boids
        @param _obstacleList The list of obstacles that the global planner needs to avoid
        @param _xSize The size of the x component of the screen
        @param _ySize The size of the y component of the screen
        @param _subGoalNumber The initial number of sample points for the global planner
        @param _screen The PyGame screen that the PRMGenerator will draw to
        """

        ## List of obstacles
        self.obstacleList = _obstacleList

        ## Position of the first goal
        self.startPos = _startPos

        ## Position of the last goal
        self.endPos = _endPos

        ## PyGame screen that is will be drawn on
        self.screen = _screen

        ## Horizontal size of the PyGame screen
        self.xSize = _xSize

        ## Vertical size of the PyGame screen
        self.ySize = _ySize

        ## Distance that the PRM is willing to check when
        ## connecting sample points
        self.adjacentThresh = 80

        ## Maximum number of sample points that can be connected
        self.numNext = 20

        ## Number of initial sample points
        self.subGoalNumber = _subGoalNumber

        ## Initial positions of the sample points
        self.subGoalPositionList = [self.startPos] + \
            self.generatePositionList(self.subGoalNumber) + \
            [self.endPos]

        ## The global roadmap. It will be a graph
        ## represented as a dictionary
        self.roadmap = dict()

        ## Holds the positions of the intermediate goals that were selected
        ## by the global path planner
        self.gPosList = list()

        ## Indexes of the goal positions
        self.goalNodes = list()
        ## Dictionary (for easy access) that holds the weights for the nodes
        self.omegaDict = dict()
        self.filterSubGoal()

        self.initOmega(self.subGoalPositionList)

    def norm(self, p1, p2):
        """
        Gets the distance between p1 and p2
        @param p1 The first point
        @param p2 The second point
        @return The Eulidean distance from p1 to p2
        """
        return np.sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2))

    def generatePositionList(self, num):
        """
        Generates the random positions for the sample points
        @param num The number of points to generate
        @return A list of random subgoals (sample points)
        """
        return [
            (
                self.getRandom(0, self.xSize),
                self.getRandom(0, self.ySize)
            ) for _ in range(num)
        ]

    def initOmega(self, posList):
        """
        Initiates the omega function which holds the node weights
        @param posList The list of positions for the sample points
        """
        omega = lambda p: (
            sum(
                map(
                    lambda ob: self.norm(p, ob.getPoint(p)),
                    self.obstacleList
                )
            )
        )
        for p in posList:
            self.omegaDict[p] = omega(p)

    def filterSubGoal(self):
        """
        Filters out sample points that are inside of obstacles
        or otherwise inadequate
        """
        delList = list()

        for i in range(len(self.subGoalPositionList)):
            for obst in self.obstacleList:
                if obst.dynamic is False:
                    dist = self.norm(
                        obst.getPoint(self.subGoalPositionList[i]),
                        self.subGoalPositionList[i]
                    )
                    if (dist < 10):
                        delList += [i]

        self.subGoalPositionList = [
            self.subGoalPositionList[j] for j in range(
                len(self.subGoalPositionList)
            ) if not j in delList
        ]

    def findNeighbors(self, point):
        """
        Finds suitable neighbours for a sample point
        """
        minList = list()
        obList = filter(
            lambda ob: self.norm(
                point,
                ob.avgPoint
            ) < self.adjacentThresh + ob.maxDist,
            self.obstacleList
        )
        sGoalList = filter(
            lambda g: self.norm(point, g[1]) < self.adjacentThresh,
            enumerate(self.subGoalPositionList)
        )
        searchList = filter(
            lambda p: not any(
                filter(
                    lambda ob: ob.detectCollision(
                        point,
                        p[1]
                    ),
                    obList
                )
            ),
            sGoalList
        )
        normList = dict()
        maxVal = self.xSize * self.ySize
        for i, j in searchList:
            normList[i] = self.norm(point, j)
        for _ in range(self.numNext):
            try:
                minPos = [
                    (i, j) for i, j in searchList if normList[i] == min(normList.values())
                ][0]
                minList += [minPos]
                normList[minPos[0]] = maxVal
            except IndexError:
                print 'balls'
        return minList

    def getRandom(self, p, q):
        """
        Gets a random number and cathes the ValueError
        if the two numbers are the same
        @param p Lower bound for the random number
        @param q upper bound for the random number
        @return A random number
        """
        try:
            return random.randint(int(p), int(q))
        except ValueError:
            return int(p)

    def generate(self, subGoalRadius):
        """
        Generates a series of random points that will become the
        roadmap and connects them and weights them into a graph.
        If the goal and the starting point are not connected, more
        points are added. The roadmap is then searched for the shortest
        weighted distance which become the intermediate goals.
        @param subGoalRadius The radius of the intermediate goals
        @return A list of sub goals from the roadmap connecting
        the starting point and the end goal
        """
        self.roadmap = dict()
        currentPos = 0
        self.dontDraw = list()
        while len(self.gPosList) <= 1:
            for i, j in enumerate(self.subGoalPositionList):
                # adds the neighbours for a certain vertex to the its sub
                # dictionary neighbours are decided by linear distance

                if i >= currentPos:
                    self.roadmap[i] = dict()
                    for p, q in self.findNeighbors(j):
                        self.roadmap[i][p] = (
                            1000 * self.norm(j, q) /
                            min(
                                self.omegaDict[j],
                                self.omegaDict[q]
                            )
                        )
                        try:
                            self.roadmap[p][i] = self.roadmap[i][p]
                        except KeyError:
                            pass

                    self.screen.fill(
                        (255, 255, 255)
                    )

                    self.draw()

                    map(
                        lambda o: o.draw(),
                        self.obstacleList
                    )
                    pygame.display.flip()
                    for e in pygame.event.get():
                        if e.type is pygame.QUIT:
                            exit()
            self.goalNodes = dijkstra.shortestPath(
                self.roadmap,
                0,
                len(self.subGoalPositionList) - 1
            )
            self.gPosList = map(
                lambda k: self.subGoalPositionList[k],
                self.goalNodes
            )
            if len(self.gPosList) == 1:
                currentPos = len(self.subGoalPositionList) - 1

                self.dontDraw += [
                    currentPos,
                    currentPos - 1,
                    currentPos + 1,
                ]

                newPosList = self.generatePositionList(
                    int(self.subGoalNumber / 2) + 1
                )
                self.initOmega(newPosList)
                self.subGoalPositionList[1: -1] += newPosList
                self.filterSubGoal()
        #print self.roadmap
        retList = map(
            lambda p: goal.CircleGoal(
                subGoalRadius,
                p,
                self.screen
            ),
            self.gPosList
        )

        retList[-1].radius = 1 * subGoalRadius
        return retList

    def getShortestPath(self, roadmap, fromNode, toNode):
        return dijkstra.shortestPath(
            roadmap,
            fromNode,
            toNode
        )

    def draw(self):
        """
        Draws the graph
        """
        map(
            lambda circ: pygame.draw.circle(
                self.screen,
                (100, 100, 100),
                circ,
                5
            ),
            self.subGoalPositionList
        )
        for k in self.roadmap.keys():
            for p in self.roadmap[k].keys():
                if not k in self.dontDraw and not p in self.dontDraw:
                    pygame.draw.line(
                        self.screen,
                        (0, 0, 0),
                        self.subGoalPositionList[k],
                        self.subGoalPositionList[p]
                    )

    def drawPath(self):
        """
        Draws the selected shortest path
        """
        pygame.draw.lines(
            self.screen,
            # (255, 255, 255),
            (0, 255, 0),
            False,
            self.gPosList,
            2
        )

        """
        for gPos in self.gPosList:
            pygame.draw.circle(
                self.screen,
                (255, 0, 255),
                gPos,
                20,
                2
            )
        """
