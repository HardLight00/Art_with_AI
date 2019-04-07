import numpy as np


class Face:
    def __init__(self, edge, children, parent):
        self.edge = edge
        self.children = children
        self.parent = parent


class Edge:
    def __init__(self, origin, face=None, next=None, previous=None):
        self.origin = origin
        self.face = face
        self.next = next
        self.previous = previous


class Point:
    def __init__(self, x, y, edge=None):
        self.x = x
        self.y = y
        self.edge = edge

    def add(self, point):
        return Point(self.x + point.x, self.y + point.y)

    def subtract(self, point):
        return Point(self.x - point.x, self.y - point.y)

    def det(self, point):
        return self.x * point.y - self.y * point.x

    def sign(self, point1, point2):
        return self.subtract(point2).det(point1.subtract(point2))

    def is_inside_triangle(self, triangle):
        a = triangle[0]
        b = triangle[1]
        c = triangle[2]

        sign1 = self.sign(a, b)
        sign2 = self.sign(b, c)
        sign3 = self.sign(c, a)

        has_neg = sign1 < 0 or sign2 < 0 or sign3 < 0
        has_pos = sign1 > 0 or sign2 > 0 or sign3 > 0

        return not (has_neg and has_pos)


    def is_inside_circle(self, circle_points):
        circle_points = sort_counter_clockwise(circle_points)

        point1 = Point(circle_points[0].x, circle_points[0].y)
        point2 = Point(circle_points[1].x, circle_points[1].y)
        point3 = Point(circle_points[2].x, circle_points[2].y)

        matrix = np.array([
            [point1.x - self.x, point2.x - self.x, point3.x - self.x],
            [point1.y - self.y, point2.y - self.y, point3.y - self.y],
            [(point1.x - self.x) ** 2 + (point1.y - self.y) ** 2,
             (point2.x - self.x) ** 2 + (point2.y - self.y) ** 2,
             (point3.x - self.x) ** 2 + (point3.y - self.y) ** 2]], dtype='float')
        return np.linalg.det(matrix) >= 0

    def is_adjacent(self, a, b, vertices):
        return (is_equal(a, vertices[0]) or is_equal(a, vertices[1]) or is_equal(a, vertices[2])) \
               and (is_equal(b, vertices[0]) or is_equal(b, vertices[1]) or is_equal(b, vertices[2])) \
               and (not is_equal(self, vertices[0]) and not is_equal(self, vertices[1])
                    and not is_equal(self, vertices[2]) and not is_line(vertices))


def is_line(triangle):
    vector1 = triangle[1].subtract(triangle[0])
    vector2 = triangle[2].subtract(triangle[0])

    det = vector1.det(vector2)
    return det == 0


def is_equal(point1, point2):
    return point1.x == point2.x and point1.y == point2.y


def is_left(a, b, c):
    vector1 = b.subtract(a)
    vector2 = c.subtract(a)

    return vector1.det(vector2) >= 0


# def is_exterior(triangle, points, boundaries):
#     vertices = get_points(triangle)
#     if boundaries is not None:
#         for i in range(0, len(boundaries)):
#             for j in range(0, len(boundaries[i])):
#                 boundary_point = points[boundaries[i][j]]
#                 if is_equal(boundary_point, vertices[0]) or is_equal(boundary_point, vertices[1]) or is_equal(
#                         boundary_point, vertices[2]):
#                     if len(boundaries[i]) < 3:
#                         return True
#
#                     if is_equal(boundary_point, vertices[0]):
#                         point1 = vertices[1]
#                         point2 = vertices[2]
#                     elif is_equal(boundary_point, vertices[1]):
#                         point1 = vertices[0]
#                         point2 = vertices[2]
#                     else:
#                         point1 = vertices[0]
#                         point2 = vertices[1]
#
#                     if j == 0:
#                         previous_point = points[boundaries[i][len(boundaries[i]) - 1]]
#                     else:
#                         previous_point = points[boundaries[i][j - 1]]
#
#                     if j == len(boundaries[i]) - 1:
#                         next_point = points[boundaries[i][0]]
#                     else:
#                         next_point = points[boundaries[i][j + 1]]
#
#                     if is_left(previous_point, boundary_point, next_point):
#                         if is_left(previous_point, boundary_point, point1) \
#                                 and is_left(previous_point, boundary_point, point2) \
#                                 and is_left(boundary_point, next_point, point1) \
#                                 and is_left(boundary_point, next_point, point2):
#                             return False
#                         else:
#                             return True
#                     else:
#                         if (is_left(previous_point, boundary_point, point1)
#                             or is_left(boundary_point, next_point, point1)) \
#                                 and (is_left(previous_point, boundary_point, point2)
#                                      or is_left(boundary_point, next_point, point2)):
#                             return False
#                         else:
#                             return True
#     return False


def is_enclosing(triangle, enclosing_points):
    for i in range(0, len(enclosing_points)):
        if is_equal(triangle[0], enclosing_points[i]) or is_equal(triangle[1], enclosing_points[i]) \
                or is_equal(triangle[2], enclosing_points[i]):
            return True
    return False


def sort_counter_clockwise(circle_points):
    vector12 = circle_points[1].subtract(circle_points[0])
    vector13 = circle_points[2].subtract(circle_points[0])

    det = vector12.det(vector13)

    if det < 0:
        circle_points[0], circle_points[2] = circle_points[2], circle_points[0]

    return circle_points


def get_points(face):
    a = face.edge.previous.origin
    b = face.edge.origin
    c = face.edge.next.origin

    return [a, b, c]


def find_triangle(face, point):
    triangle_list = []

    if not point.is_inside_triangle(get_points(face)):
        return triangle_list

    if len(face.children) < 1:
        return [face]

    for i in range(0, len(face.children)):
        if face.children[i] is not None:
            child = face.children[i]
            triangle = find_triangle(child, point)
            for j in range(0, len(triangle)):
                triangle_list += [triangle[j]]

    return triangle_list


def compute_triangulation(points, vertices=None, edges=None, faces=None):
    if vertices is None:
        vertices = []
    if edges is None:
        edges = []
    if faces is None:
        faces =[]

    min_x = -1
    min_y = -1

    max_x = 1024
    max_y = 1024

    # min_x = points[0].x
    # min_y = points[0].y
    #
    # max_x = points[0].x
    # max_y = points[0].y

    # for i in range(0, len(points)):
    #     if points[i].x < min_x:
    #         min_x = points[i].x
    #     if points[i].y < min_y:
    #         min_y = points[i].y
    #     if points[i].x > max_x:
    #         max_x = points[i].x
    #     if points[i].y > max_y:
    #         max_y = points[i].y

    point1 = Point(min_x, min_y)
    point2 = Point(max_x + (max_y - min_y), min_y)
    point3 = Point(min_x, max_y + (max_x - min_x))

    is_in_points1 = 0
    is_in_points2 = 0
    is_in_points3 = 0

    for i in range(0, len(points)):
        if is_equal(points[i], point1):
            is_in_points1 = 1
        if is_equal(points[i], point2):
            is_in_points2 = 1
        if is_equal(points[i], point3):
            is_in_points3 = 1

    enclosing_points = []

    if is_in_points1 == 0:
        enclosing_points += [point1]

    if is_in_points2 == 0:
        enclosing_points += [point2]

    if is_in_points3 == 0:
        enclosing_points += [point3]

    points += [point1]
    points += [point2]
    points += [point3]

    vertices += [[], [], []]
    edges += [[], [], []]
    faces += [[]]
    j = -3

    for i in range(len(points) - 3, len(points)):
        vertices[len(vertices) + j] = Point(points[i].x, points[i].y)
        edges[len(edges) + j] = Edge(origin=vertices[j])
        faces[len(faces) - 1] = Face(edge=edges[0], children=[], parent=[])
        vertices[j].edge = edges[j]
        edges[j].face = faces[0]
        j += 1

    edges[len(edges) - 3].next = edges[len(edges) - 2]
    edges[len(edges) - 3].previous = edges[len(edges) - 1]
    edges[len(edges) - 2].next = edges[len(edges) - 1]
    edges[len(edges) - 2].previous = edges[len(edges) - 3]
    edges[len(edges) - 1].next = edges[len(edges) - 3]
    edges[len(edges) - 1].previous = edges[len(edges) - 2]

    for i in range(0, len(points) - 3):
        triangle = find_triangle(faces[0], points[i])
        if len(triangle) == 1 or len(triangle) == 2:
            triangle_queue = []
            vertices += [Point(points[i].x, points[i].y)]
            vert = vertices[len(vertices) - 1]
            edges_len = len(edges)

            for m in range(0, len(triangle)):
                vert1 = triangle[m].edge.origin
                vert2 = triangle[m].edge.next.origin
                vert3 = triangle[m].edge.previous.origin

                edges += [Edge(origin=vert1)]
                edges += [Edge(origin=vert2)]
                edges += [Edge(origin=vert)]

                edges_len += 3

                edges += [Edge(origin=vert2)]
                edges += [Edge(origin=vert3)]
                edges += [Edge(origin=vert)]

                edges_len += 3

                edges += [Edge(origin=vert3)]
                edges += [Edge(origin=vert1)]
                edges += [Edge(origin=vert)]

                for j in range(edges_len - 6, edges_len + 1, 3):
                    vert1.edge = edges[j]
                    vert2.edge = edges[j + 1]
                    vert.edge = edges[j + 2]

                    edges[j].next = edges[j + 1]
                    edges[j].previous = edges[j + 2]
                    edges[j + 1].next = edges[j + 2]
                    edges[j + 1].previous = edges[j]
                    edges[j + 2].next = edges[j]
                    edges[j + 2].previous = edges[j + 1]

                    faces += [Face(edge=edges[j], children=[], parent=[triangle[m]])]

                    edges[j].face = faces[len(faces) - 1]
                    edges[j + 1].face = faces[len(faces) - 1]
                    edges[j + 2].face = faces[len(faces) - 1]

                    triangle_queue.append(len(faces) - 1)

                    triangle[m].children += [faces[len(faces) - 1]]

            while len(triangle_queue) > 0:
                point = points[i]
                index = triangle_queue.pop()
                current_triangle_points = get_points(faces[index])

                if is_equal(current_triangle_points[0], point):
                    point1 = current_triangle_points[1]
                    point2 = current_triangle_points[2]
                elif is_equal(current_triangle_points[1], point):
                    point1 = current_triangle_points[0]
                    point2 = current_triangle_points[2]
                else:
                    point1 = current_triangle_points[0]
                    point2 = current_triangle_points[1]

                if not is_line(current_triangle_points):
                    for f in range(len(faces) - 1, -1, -1):
                        if faces[f] is not None:
                            current_face_points = get_points(faces[f])
                            if point.is_adjacent(point1, point2, current_face_points) and len(faces[f].children) == 0:

                                if is_equal(point1, current_face_points[0]) \
                                        and is_equal(point2, current_face_points[1]) \
                                        or is_equal(point2, current_face_points[0]) and is_equal(point1,
                                                                                                 current_face_points[
                                                                                                     1]):
                                    point3 = current_face_points[2]
                                elif is_equal(point1, current_face_points[2]) and is_equal(point2,
                                                                                           current_face_points[1]) \
                                        or is_equal(point2, current_face_points[2]) and is_equal(point1,
                                                                                                 current_face_points[
                                                                                                     1]):
                                    point3 = current_face_points[0]
                                else:
                                    point3 = current_face_points[1]

                                if point.is_inside_circle(current_face_points):
                                    parents = [faces[f], faces[index]]

                                    edges_len = len(edges)

                                    edges += [Edge(origin=point)]
                                    edges += [Edge(origin=point1)]
                                    edges += [Edge(origin=point3)]

                                    edges[edges_len].next = edges[edges_len + 1]
                                    edges[edges_len].previous = edges[edges_len + 2]
                                    edges[edges_len + 1].next = edges[edges_len + 2]
                                    edges[edges_len + 1].previous = edges[edges_len]
                                    edges[edges_len + 2].next = edges[edges_len]
                                    edges[edges_len + 2].previous = edges[edges_len + 1]

                                    faces += [Face(edge=edges[edges_len], children=[], parent=parents)]

                                    edges[edges_len].face = faces[len(faces) - 1]
                                    edges[edges_len + 1].face = faces[len(faces) - 1]
                                    edges[edges_len + 2].face = faces[len(faces) - 1]

                                    edges_len += 3

                                    edges += [Edge(origin=point)]
                                    edges += [Edge(origin=point2)]
                                    edges += [Edge(origin=point3)]

                                    edges[edges_len].next = edges[edges_len + 1]
                                    edges[edges_len].previous = edges[edges_len + 2]
                                    edges[edges_len + 1].next = edges[edges_len + 2]
                                    edges[edges_len + 1].previous = edges[edges_len]
                                    edges[edges_len + 2].next = edges[edges_len]
                                    edges[edges_len + 2].previous = edges[edges_len + 1]

                                    faces += [Face(edge=edges[edges_len], children=[], parent=parents)]

                                    edges[edges_len].face = faces[len(faces) - 1]
                                    edges[edges_len + 1].face = faces[len(faces) - 1]
                                    edges[edges_len + 2].face = faces[len(faces) - 1]

                                    faces[f].children += [faces[len(faces) - 1]]
                                    faces[f].children += [faces[len(faces) - 2]]
                                    faces[index].children += [faces[len(faces) - 1]]
                                    faces[index].children += [faces[len(faces) - 2]]

                                    triangle_queue.append(len(faces) - 1)
                                    triangle_queue.append(len(faces) - 2)
                                break
    return vertices, edges, faces, enclosing_points
