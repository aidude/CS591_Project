__author__ = "amritansh"

import boidsimulation as bs
import sys
import random

"""
Main module to run for testing purposes
"""

if __name__ == "__main__":
    mapDict = {
        "maps/scene2.map": {
            "startPoint": (494, 213),
            "endPoint": (404, 20)
        },
        "maps/scene3.map": {
            "startPoint": (356, 42),
            "endPoint": (852, 450)
        },
        "maps/scene1.map": {
            "startPoint": (50, 50),  # (50, 600)
            "endPoint": (980, 30)
        },
        "maps/empty.map": {
            "startPoint": (50, 50),  # (50, 600)
            "endPoint": (980, 590)
        },
        "maps/s.map": {
            "startPoint": (0, 80),  # (50, 600)
            "endPoint": (980, 90)
        },
        "maps/maze.map": {
            "startPoint": (50, 50),  # (50, 600)
            "endPoint": (950, 30)
        },
        "maps/maze2.map": {
            "startPoint": (50, 70),  # (50, 600)
            "endPoint": (950, 30)
        },
        "maps/great_divide.map": {
            "startPoint": (50, 70),
            "endPoint": (950, 500)
        },
        "maps/random.map": {
            "startPoint": (60, 60),
            "endPoint": (950, 360)
        },
        "maps/hurdles.map": {
            "startPoint": (60, 270),
            "endPoint": (950, 270)
        }
    }

    if len(sys.argv) <= 2:
        print("Not enough commandline args!")
        print("Need at least 2 commands!")
    else:
        flockSize = int(sys.argv[2])
        startPoint = mapDict[sys.argv[1]]["startPoint"]
        endPoint = mapDict[sys.argv[1]]["endPoint"]
        mapFilePath = sys.argv[1]
        obstacleFilePath = None
        dynamicObstacleAutoGenerate = False
        generateTarget = 0

        if len(sys.argv) >= 4:
            arg = sys.argv[3]
            if (arg.isdigit()):
                dynamicObstacleAutoGenerate = True
                generateTarget = int(arg)
            else:
                obstacleFilePath = arg

            randomSeed = sys.argv[4]
            if randomSeed:
                print "SEED RANDOM: ", randomSeed
                random.seed(randomSeed)

        fs = bs.FlockSim(
            flockSize,
            startPoint,
            endPoint,
            map_file=mapFilePath,
            obstacle_file=obstacleFilePath,
            auto_gen_obst=dynamicObstacleAutoGenerate,
            auto_gen_number=generateTarget,
            random_seed=randomSeed
        )
        fs.animate()
