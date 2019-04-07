import copy
import math
import random
import sys
import tempfile

from PIL import Image
from PIL import ImageDraw

import triangulation
from triangulation import compute_triangulation, Point

COLOUR_BLACK = (0, 0, 0, 255)
OFFSET = 2
MIN_MUTATION_POINTS = 5
MAX_MUTATION_POINTS = 25
POINTS_NUM = 50


class Triangulation:
    def __init__(self, points, vertices=None, edges=None, faces=None):
        if vertices is not None and edges is not None and faces is not None:
            (vertices, edges, faces, enclosing_points) = triangulation.compute_triangulation(points=points,
                                                                                             vertices=vertices,
                                                                                             edges=edges, faces=faces)
        else:
            (vertices, edges, faces, enclosing_points) = triangulation.compute_triangulation(points=points)
        self.vertices = vertices
        self.edges = edges
        self.faces = faces
        self.enclosing_points = enclosing_points
        # self.color = [generate_color(img, triangle) for triangle in self.get_triangles()]

    def get_triangles(self):
        output_triangles = []
        for i in range(0, len(self.faces)):
            if self.faces[i] is not None:
                three_points = triangulation.get_points(self.faces[i])
                num_children = len(self.faces[i].children)
                is_it_line = triangulation.is_line(three_points)
                is_it_enclosing = triangulation.is_enclosing(three_points, self.enclosing_points)
                if num_children == 0 and not is_it_line \
                        and not is_it_enclosing:
                    output_triangles += [three_points]
        return output_triangles

    def generate_points_in_triangles(self, number):
        triangles = self.get_triangles()
        new_points = []
        for i in range(0, number):
            index = random.randrange(0, len(triangles) - 1)
            x = triangles[index][0].x + triangles[index][1].x + triangles[index][2].x
            y = triangles[index][0].y + triangles[index][1].y + triangles[index][2].y
            new_points += [Point(x / 3, y / 3)]
        return new_points


class DNA(object):
    def __init__(self, img, points, triangulations):
        self.img = img
        self.points = points
        self.triangulations = triangulations
        self.generation = 0

    def draw(self, background=COLOUR_BLACK, show=False, save=False, generation=None, folder_name=None):
        if folder_name is None:
            folder_name = "default"
        size = self.img.size
        img = Image.new('RGB', size, background)
        draw = Image.new('RGBA', size)
        p_draw = ImageDraw.Draw(draw)
        for triangle in self.triangulations.get_triangles():
            color = generate_color(self.img, triangle)
            points = [(point.x, point.y) for point in triangle]
            p_draw.polygon(points, fill=color, outline=color)
            img.paste(draw, mask=draw)

        if show:
            img.show()

        if save:
            temp_name = u"art0000{}".format(generation)
            out_path = u"./img/triangulation_res/{}/{}.png".format(folder_name, temp_name)
            # img = img.filter(ImageFilter.GaussianBlur(radius=3))
            img.save(out_path)
            print(u"saving image to {}".format(out_path))

        return img

    def mutate(self):
        num_points = random.randrange(MIN_MUTATION_POINTS, MAX_MUTATION_POINTS + 1)
        new_points = self.triangulations.generate_points_in_triangles(num_points)
        triangulation = Triangulation(new_points, self.triangulations.vertices, self.triangulations.edges,
                                      self.triangulations.faces)

        return DNA(self.img, new_points, triangulation)


def fitness(img_1, img_2):
    fitness = 0.0
    for y in range(0, img_1.size[1]):
        for x in range(0, img_1.size[0]):
            r1, g1, b1 = img_1.getpixel((x, y))
            r2, g2, b2 = img_2.getpixel((x, y))
            d_r = r1 - r2
            d_b = b1 - b2
            d_g = g1 - g2
            pixel_fitness = math.sqrt(d_r ** 2 + d_g ** 2 + d_b ** 2)
            fitness += pixel_fitness
    return fitness


def generate_point(width, height):
    x = random.randrange(0 + OFFSET, width - OFFSET, 1)
    y = random.randrange(0 + OFFSET, height - OFFSET, 1)
    return Point(x, y)


def generate_color(img, triangle):
    pix = img.load()
    sum_pix = [0, 0, 0]
    count = 0
    for i in range(0, 10):
        for j in range(0, 10 - i):
            x = triangle[0].x * i + triangle[1].x * j + triangle[2].x * (10 - i - j)
            y = triangle[0].y * i + triangle[1].y * j + triangle[2].y * (10 - i - j)
            point = Point(x // 10, y // 10)
            sum_pix[0] = sum_pix[0] + pix[point.x, point.y][0]
            sum_pix[1] = sum_pix[1] + pix[point.x, point.y][1]
            sum_pix[2] = sum_pix[2] + pix[point.x, point.y][2]
            count += 1
    avg_pix = (sum_pix[0] // count, sum_pix[1] // count, sum_pix[2] // count)
    return avg_pix


# def generate_color(img, triangle):
#     sum_point = triangle[0].add(triangle[1]).add(triangle[2])
#     avg_point = Point(sum_point.x / 3, sum_point.y / 3)
#     pix = img.load()
#     (width, height) = img.size
#     while avg_point.x > width:
#         avg_point.x /= 2
#
#     while avg_point.y > height:
#         avg_point.y /= 2
#
#     return pix[avg_point.x, avg_point.y]


def generate_dna(img):
    (width, height) = img.size
    points = [generate_point(width, height) for point in range(POINTS_NUM - 4)]
    x = 0
    y = 0
    while x < width:
        while y < height:
            points += [Point(x, y)]
            y += random.randrange(0, height // 10)
        x += random.randrange(0, width // 10)

    x = 0
    y = 0
    while y < height:
        while x < width:
            points += [Point(x, y)]
            x += random.randrange(0, width // 10)
        y += random.randrange(0, height // 10)

    x = width - 1
    y = height - 1
    while x > 0:
        while y > 0:
            points += [Point(x, y)]
            y -= random.randrange(0, height // 10)
        x -= random.randrange(0, width // 10)

    x = width - 1
    y = height - 1
    while y > 0:
        while x > 0:
            points += [Point(x, y)]
            x -= random.randrange(0, width // 10)
        y -= random.randrange(0, height // 10)

    # for x in range(0, width, width // 10):
    #     for y in range(0, height, height // 10):
    #         points += [Point(x, y)]
    triangulations = Triangulation(points=points)

    return DNA(img, points, triangulations)


def main(argv):
    if len(argv) < 3:
        sys.exit(1)

    folder_name = argv[1]
    path_to_img = argv[2]

    img = Image.open(path_to_img)
    dna = generate_dna(img)
    parent = dna.draw(show=False)
    fitness_parent = fitness(img, parent)

    generations = pic_nr = 0
    while generations < 200:
        dna_mutated = dna.mutate()
        child = dna_mutated.draw(show=False)
        fitness_child = fitness(img, child)
        if fitness_child < fitness_parent:
            dna = dna_mutated
            fitness_parent = fitness_child

            generations += 1
            # print("generation {}".format(generations))
            # if generations % 100 == 0:
            #     print(u"showing generation {}".format(generations))
            #     pic_nr += 1
            dna.draw(show=False, save=True, generation=generations, folder_name=folder_name)
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)
