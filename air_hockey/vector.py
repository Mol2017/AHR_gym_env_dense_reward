import numpy as np

# 单位化向量
magnitude = np.linalg.norm
address_limit = 1e-6


def normalize(array):
    mag = magnitude(array)
    if mag != 0.0:
        array /= mag
    return array


def address_data(array1):
    array2 = np.copy(array1)
    for index, data in enumerate(array1):
        if abs(array1[index]) < address_limit:
            array2[index] = 0
        else:
            pass
    return array2
