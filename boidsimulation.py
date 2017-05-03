__author__ = "amritansh"

import pygame
import configuration
import time


class FlockSim:
    """
    Main class for that is used for the simulation and display of the flock.
    It also is used to gather statistics about the flock and present them
    in a useful manner.
    """
    def __init__(
        self,
        flockSize,
        startPoint,
        endPoint,
        **kwargs
    ):
        """
        Initializes the flock and the display mechanism (PyGame)
        @param flockSize The size of the flock (number of boids)
        @param startPoint The macro starting position of the flock
        @param endPoint The last goal point for the flock
        @param _mapFile The file containing details about the obstacles
        @param _dataFile The file that the data will be exported to
        """
        pygame.init()

        ## Tells if the flock has reached the end goal (used again
        ## to see if the escape or space bar were hit to stop the rendering)
        self.done = False

        ## Defines the color black
        self.BLACK = (0, 0, 0)

        ## Defines the color white
        self.WHITE = (255, 255, 255)

        ## The font that is used for displaying the frame number
        self.font = pygame.font.Font(None, 50)

        ## The dimensions of the PyGame screen
        self.dim = xSize, ySize = 1000, 600

        ## The configuration object (in this case the configuration
        ## is defined by an exterior file)
        self.config = configuration.PolyFileConfiguration()

        ## The starting point of the flock
        self.sPos = startPoint

        ## The position of the last goal for the flock
        self.ePos = endPoint

        ## Variable used to store the list of surfaces for simulation playback
        self.surfaceList = list()

        ## Maximum number of iterations
        self.iterations = 800

        ## Counts which frame the user is on for the playback (don't know why
        ## it is set to -2, it just works)
        self.frameCounter = -2

        ## Global counter used for the rendering and the playback
        self.counter = 0

        ## The size of the flock (number of boids)
        self.flockSize = flockSize

        ## The file that contains the data about the obstacles
        self.mapFile = kwargs.get("map_file", None)

        ## The file that the statistics data will be written to
        self.dataFile = kwargs.get("data_file", None)

        ## File containing the obstacles map points
        self.obstacleFile = kwargs.get("obstacle_file", None)

        ## Auto Generate Random obstacles Flag
        self.auto_gen_obst = kwargs.get("auto_gen_obst", False)

        ## Number of random dynamic obstacles to generate
        self.auto_gen_number = kwargs.get("auto_gen_number", 0)

        self.random_seed = kwargs.get("random_seed", None)

    def avg(self, l):
        """
        Gets the average of a list
        @param l The list to be averaged
        @return l The average value in list l
        """
        try:
            return sum(l) / len(l)
        except ZeroDivisionError:
            return 0

    def getStats(self):
        """
        Gets runtime statistics about the simulation and writes it to a file.
        Currently, the statistics being gathered are the current time that has
        passed, the average distance between the boids, the average minimum
        distance between the boids, and the number of boids that have finished
        """
        endTime = time.time()
        avgList = list()
        minAvgList = list()
        for b_1 in self.config.boidList:
            distList = list()
            for b_2 in self.config.boidList:
                if b_1 != b_2:
                    distList += [b_1.norm(b_1.position, b_2.position)]
            try:
                minAvgList += [min(distList)]
            except ValueError:
                minAvgList += distList
            avgList += [self.avg(distList)]

        avgMinVal = self.avg(minAvgList)
        avgDistVal = self.avg(avgList)

        stuck_counter = 0
        for boid in self.config.boidList:
            stuck_counter += boid.stuck_counter

        # writes data to the file
        self.dataFile.write(
            "current_step: " + str(self.counter) +
            ", current_time: " + str(endTime - self.startTime) +
            ", average_distance: " + str(avgDistVal) +
            ", average_min_distance: " + str(avgMinVal) +
            ", number_finished: " + str(self.numInGoal) +
            ", stuck: " + str(stuck_counter) +
            "\n"
        )

    def getBoidData(self):
        """
        Writes all of the boid positions to a file
        """
        self.dataFile.write(
            str(self.flockSize) +
            "\n"
        )
        for b_num, b in enumerate(self.config.boidList):
            self.dataFile.write(
                "boid_" + str(b_num) + " : " +
                str(
                    tuple(
                        map(
                            int,
                            b.position
                        )
                    )
                ) + " | "
            )
        self.dataFile.write("\n")

    def animate(self):
        """
        Renders and then allows interactive playback of the swarm
        simulation data
        """
        self.render(True)
        self.play()

    def init_prm(self):
        """
        Initializes the PRM generator used for the global planner. Also sets
        the boid list for the rest of the flock
        """
        self.config.initVars(
            self.sPos,
            self.ePos,
            self.flockSize,
            map_file=self.mapFile,
            dynamic_obstacles=self.obstacleFile,
            auto_gen_obst=self.auto_gen_obst,
            auto_gen_number=self.auto_gen_number
        )

        if self.dataFile:
            self.dataFile = open(self.dataFile, "w")
            #print self.dataFile
            self.dataFile.truncate()

        map(
            lambda b: b.setBoidList(self.config.boidList),
            self.config.boidList
        )

    def render(self, forPlay=False):
        """
        Renders the scene. This means that the time taken for the boids to
        reach the goal in this function is that actual amount of computational
        time needed.
        @param forPlay Specifies if the surface data should be
        recorded for animation
        """
        self.init_prm()
        pygame.display.set_caption('Rendering...')
        #print 'I am working, I promise'
        self.startTime = time.time()
        while not self.done and self.counter < self.iterations:
            self.frameCounter += 1
            frame = pygame.Surface(
                (
                    self.config.xSize,
                    self.config.ySize
                )
            )
            self.config.screen.fill(self.WHITE)
            boidPosList = [
                b.position for b in self.config.boidList
            ]
            boidHeadingList = [
                b.heading for b in self.config.boidList
            ]

            # updates the boids and gathers the statistics
            map(lambda o: o.draw(), self.config.obstacleList)
            map(lambda b: b.draw(), self.config.boidList)
            map(lambda b: b.update(), self.config.boidList)
            self.numInGoal = len(
                filter(
                    lambda b: b.goalCounter == len(b.goalList) - 1,
                    self.config.boidList
                )
            )
            if self.dataFile is not None:
                #self.getBoidData()
                self.getStats()

            #map(lambda g: g.draw(), self.config.goalList)
            self.config.prmGen.drawPath()

            frame.blit(self.config.screen, (0, 0))
            if forPlay:
                self.surfaceList += [frame]
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                self.done = True
            for e in pygame.event.get():
                if e.type is pygame.QUIT:
                    exit()
            self.counter += 1
            pygame.display.flip()

            if self.numInGoal == self.flockSize:
                self.done = True


    def play(self):
        """
        Plays the scene after it has rendered. Iterates through
        surfaces that have been stored in surfaceList and blits
        the new surface on the screen
        """
        self.config.screen.fill(self.WHITE)
        pygame.display.set_caption('Playing...')
        self.counter = 0
        self.done = False
        while not self.done:
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                self.counter -= 1
                time.sleep(0.04)
            elif key[pygame.K_RIGHT]:
                self.counter += 1
                time.sleep(0.04)
            elif key[pygame.K_ESCAPE]:
                exit()

            #constrains the self.counter
            if self.counter > len(self.surfaceList)-1:
                self.counter = len(self.surfaceList)-1
            elif self.counter < 0:
                self.counter = 0
            self.config.screen.blit(
                self.surfaceList[self.counter],
                (0, 0)
            )
            text = self.font.render(
                'Frame: ' + str(self.counter),
                0,
                self.BLACK
            )
            self.config.screen.blit(text, (0, 0))

            # if self.random_seed:
                # random_seed = self.font.render(
                #     'Random Seed: ' + str(self.random_seed),
                #     0,
                #     self.BLACK
                # )
                # self.config.screen.blit(random_seed, (0, 30))

            pygame.display.flip()
            for e in pygame.event.get():
                if e.type is pygame.QUIT:
                    exit()

if __name__ == '__main__':
    FlockSim(
        30,
        (356, 42),
        (852, 450)
    ).animate()
