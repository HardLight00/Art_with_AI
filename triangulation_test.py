import triangulation

points = [triangulation.Point(0, 0),
          triangulation.Point(10, 0),
          triangulation.Point(5, 5),
          triangulation.Point(0, 5),
          triangulation.Point(15, 6),
          triangulation.Point(20, 15),
          triangulation.Point(2, 10),
          triangulation.Point(4, 12),
          triangulation.Point(30, 10),
          triangulation.Point(18, 20)]
(vertices, edges, faces, enclosing_points) = triangulation.compute_triangulation(points)

points = [triangulation.Point(20, 40),
          triangulation.Point(3, 25),
          triangulation.Point(24, 14),
          triangulation.Point(6, 3),
          triangulation.Point(10, 23)]

(vertices, edges, faces, enclosing_points) = triangulation.compute_triangulation(points=points, vertices=vertices,
                                                                                 edges=edges, faces=faces)

output_triangles = []
for i in range(0, len(faces)):
    if faces[i] is not None:
        three_points = triangulation.get_points(faces[i])
        num_children = len(faces[i].children)
        is_it_line = triangulation.is_line(three_points)
        is_it_enclosing = triangulation.is_enclosing(three_points, enclosing_points)
        if num_children == 0 and not is_it_line \
                and not is_it_enclosing:
            output_triangles += [three_points]
print("result:")
for triangle in output_triangles:
    print("triangle:")
    print("\tvert1: x: {}, y: {}".format(triangle[0].x, triangle[0].y))
    print("\tvert2: x: {}, y: {}".format(triangle[1].x, triangle[1].y))
    print("\tvert3: x: {}, y: {}".format(triangle[2].x, triangle[2].y))
print("#triangles: " + str(len(output_triangles)))
