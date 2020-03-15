import numpy as np
from scipy.ndimage.measurements import label
from scipy.ndimage.morphology import generate_binary_structure
from . import constants

MAIN_STRUCTURE = generate_binary_structure(2, 2)
MAIN_STRUCTURE = np.ones((3, 3), dtype=np.int)

def construct_paths(image: np.array):
    global MAIN_STRUCTURE
    labeled_array, num_features = label(image, structure=MAIN_STRUCTURE)

    indices = np.indices(image.shape).T[:, :, [1, 0]]

    return [indices[labeled_array.T == i + 1] for i in range(num_features)]


def path_generator(image: np.array):
    height, width = image.shape
    paths = construct_paths(image)
    for path in paths:
        n_connected_points = len(path)
        for i, (x, y) in enumerate(path):
            x *= constants.PIXEL_FACTOR
            y = (height - y) * constants.PIXEL_FACTOR
            if i == 0:
                yield [x, y, 1]
                yield [x, y, 0]
            elif i == n_connected_points - 1:
                yield [x, y, 0]
                yield [x, y, 1]
            else:
                yield [x, y, 0]
