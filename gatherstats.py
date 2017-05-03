__author__ = "amritansh"

import sys

import boidsimulation as bs

# GLOBAL VARS
iterations = 1


# generates stats for the project
def generateStats(mapFile, iterations, startPoint, endPoint):
    """
    Generates the statistics and saves them in a well known
    location

    """
    getFileFormat = lambda boids, obstacles, it: str(
        "stats/" +
        mapFile.split("/")[-1].split(".")[0] +
        "_" + str(boids) + "_" + str(obstacles) + "_" + str(it)
    )

    for boids in [90]:
        for obstacles in [15]:
            for i in range(iterations):
                #reload(bs)
                print mapFile, " : ", boids, ":", obstacles, ":", i
                dFile = getFileFormat(boids, obstacles, i)

                while True:
                    try:
                        fSim = bs.FlockSim(
                            boids,
                            startPoint,
                            endPoint,
                            map_file=mapFile,
                            obstacle_file=None,
                            auto_gen_obst=True,
                            auto_gen_number=obstacles,
                            data_file=dFile
                        )
                        fSim.render()
                        break
                    except ZeroDivisionError:
                        print("Rerunning!")

## A list of dictionaries used to store the map files,
#starting and ending points of the boids
test_list = [
    #{
    #    "filename": "maps/scene2.map",
    #    "startPoint": (494, 213),
    #    "endPoint": (404, 20)
    #},
    # {
    #     "filename": "maps/scene3.map",
    #     "startPoint": (356, 42),
    #     "endPoint": (852, 450)
    # },
    # {
    #     "filename": "maps/scene1.map",
    #     "startPoint": (50, 600),
    #     "endPoint": (980, 30)
    # },
    # {
    #     "filename": "maps/s.map",
    #     "startPoint": (50, 50),  # (50, 600)
    #     "endPoint": (980, 30)
    # },
    # {
    #     "filename": "maps/maze.map",
    #     "startPoint": (50, 50),  # (50, 600)
    #     "endPoint": (950, 30)
    # },
    {
        "filename": "maps/maze2.map",
        "start_point": (50, 70),  # (50, 600)
        "end_point": (950, 30)
    },
    {
        "filename": "maps/great_divide.map",
        "start_point": (50, 70),
        "end_point": (950, 500)
    },
    {
        "filename": "maps/hurdles.map",
        "start_point": (60, 270),
        "end_point": (950, 270)
    }
]

if __name__ == "__main__":
    test = test_list[int(sys.argv[1])]

    filename = test["filename"]
    start_point = test["start_point"]
    end_point = test["end_point"]

    generateStats(filename, iterations, start_point, end_point)
