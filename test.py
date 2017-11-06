import numpy

vertices = [

    [2, -2, 0],
    [-2, -2, 0],
    [-2, 2, 0],

    [2, -2, 0],
    [-2, 2, 0],
    [2, 2, 0],

    [0, 0, 4],
    [-2, -2, 0],
    [2, -2, 0],

    [-2, -2, 0],
    [0, 0, 4],
    [-2, 2, 0],

    [-2, 2, 0],
    [0, 0, 4],
    [2, 2, 0],

    [0, 0, 4],
    [2, -2, 0],
    [2, 2, 0]

]

triangles = numpy.reshape(vertices, [-1, 3, 3])
triangle_slopes = []

for triangle in triangles:
    n = numpy.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
    nn = n / numpy.linalg.norm(n)
    z_angle = numpy.arccos(abs(nn[2]))
    triangle_slopes.append(z_angle)

layer_steps = [0.2, 0.15, 0.1, 0.06]
max_layers = 1000
z_level = 0
absolute_heights = []
layer_output = []

for layer_index in range(0, max_layers):
    if layer_index != 0:
        z_level = absolute_heights[layer_index - 1]

    triangles_of_interest = []
    triangle_indices = []

    for layer_step in layer_steps:
        triangles_of_interest = numpy.where(triangles[::, ::, 2::] >= z_level)

        if len(triangles_of_interest[0]) == 0:
            break

        triangle_indices = numpy.array(numpy.unique(triangles_of_interest[0]))
        slopes = numpy.array(triangle_slopes)[triangle_indices]
        minimum_slope = min(slopes)
        slope_tan = numpy.tan(minimum_slope)

        if (slope_tan > 0 and layer_step / slope_tan <= 0.1) or layer_step == min(layer_steps):
            absolute_heights.append(z_level + layer_step)
            layer_output.append({
                "layer_height": str(layer_step),
                "absolute_height": str(round(z_level + layer_step, 2)),
                "layer_slope": str(round(minimum_slope, 2)),
                "triangle_count": str(len(triangles_of_interest))
            })
            break

    if len(triangles_of_interest[0]) == 0:
        break

print("done", layer_output)
