import numpy as np
from scipy.ndimage.measurements import label
from scipy.ndimage.morphology import generate_binary_structure

MAIN_STRUCTURE = generate_binary_structure((2, 2))


def construct_paths(image: np.array):
    global MAIN_STRUCTURE

    labeled_array, num_features = label(image, structure=MAIN_STRUCTURE)

    indices = np.indices(image.shape).T[:, :, [1, 0]]

    return [indices[labeled_array == i + 1] for i in range(num_features)]


def path_generator(image: np.array):
    paths = construct_paths(image)
    for path in paths:
        n_connected_points = len(path)
        for i, (x, y) in enumerate(path):
            if i == 0:
                yield [x, y, 1]
                yield [x, y, 0]
            elif i == n_connected_points - 1:
                yield [x, y, 0]
                yield [x, y, 1]
            else:
                yield [x, y, 0]
