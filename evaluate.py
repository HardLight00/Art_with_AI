import matplotlib as matplotlib
from PIL import Image
import matplotlib.pyplot as plt

from main import fitness


def compare_fitness(copy_folder, style):
    f = open("report-{}.txt".format(copy_folder), "r")

    line = f.readline()
    generation = []
    fitness = []
    while line is not None and len(line) > 2:
        param = line.split(", ")
        generation += [int(param[0].split(" ")[1])]
        fitness += [float(param[1].split(" ")[1].split("\n")[0])]
        print(generation[len(generation) - 1])
        line = f.readline()
    plt.plot(generation, fitness, style)
    f.close()
    # plt.plot(fits, style)


compare_fitness("piter_griffin", 'bo')
compare_fitness("griffin", 'b^')
compare_fitness("chessboard", 'go')
compare_fitness("cv", 'ro')
compare_fitness("cv2", 'r^')
compare_fitness("tron", 'mo')
compare_fitness("tron2", 'm^')
plt.show()
