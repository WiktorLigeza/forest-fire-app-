import numpy as np
import random

def any_black_neighbour(data, i, j):
    if data[i - 1][j - 1] == 0 or data[i][j - 1] == 0 or data[i + 1][j - 1] == 0 or \
            data[i - 1][j] == 0 or data[i][j] == 0 or data[i + 1][j] == 0 or \
            data[i - 1][j + 1] == 0 or data[i][j + 1] == 0 or data[i + 1][j + 1] == 0:
        return True
    else:
        return False


def any_white_neighbour(data, i, j):
    if data[i - 1][j - 1] == 255 or data[i][j - 1] == 255 or data[i + 1][j - 1] == 255 or \
            data[i - 1][j] == 255 or data[i][j] == 255 or data[i + 1][j] == 255 or \
            data[i - 1][j + 1] == 255 or data[i][j + 1] == 255 or data[i + 1][j + 1] == 255:
        return True
    else:
        return False


def get_sum(data, i, j, k):
    s = (data[i - 1][j - 1] * k[0][0]) + (data[i][j - 1] * k[1][0]) + (data[i + 1][j - 1] * k[2][0]) + \
        (data[i - 1][j] * k[0][1]) + (data[i][j] * k[1][1]) + (data[i + 1][j] * k[2][1]) + \
        (data[i - 1][j + 1] * k[0][2]) + (data[i][j + 1] * k[1][2]) + (data[i + 1][j + 1] * k[2][2])
    if s > 255: s = 255
    if s < 0: s = 0

    return s


def binarize(data, threshold):
    binary = (data > threshold) * 255
    return binary


def dilation(data):
    x = np.shape(data)[0]
    y = np.shape(data)[1]
    output = np.copy(data)
    for i in range(1, x - 1):
        for j in range(1, y - 1):
            if data[i][j] == 255:
                if any_black_neighbour(data, i, j):
                    output[i][j] = 0
    return output


def erosion(data):
    x = np.shape(data)[0]
    y = np.shape(data)[1]
    output = np.copy(data)
    for i in range(1, x - 1):
        for j in range(1, y - 1):
            if data[i][j] == 0:
                if any_white_neighbour(data, i, j):
                    output[i][j] = 255

    return output


def conv(data, kernel):
    x = np.shape(data)[0]
    y = np.shape(data)[1]
    output = np.copy(data)
    for i in range(1, x - 1):
        for j in range(1, y - 1):
            output[i][j] = get_sum(data, i, j, kernel)

    return output


def oneD_cellular_automata(rule, width, option):
    # create binary representation of given rule value
    bin_rep = [int(x) for x in np.binary_repr(rule, width=8)]

    # set binary matrix
    bin_pat = np.array([[1., 1., 1.],
                        [1., 1., 0.],
                        [1., 0., 1.],
                        [1., 0., 0.],
                        [0., 1., 1.],
                        [0., 1., 0.],
                        [0., 0., 1.],
                        [0., 0., 0.]])

    # set size
    height = int(width)

    # create blank matrix with one seed int the middle of the first row
    canvas = np.zeros([height, width + 2])
    canvas[0, int(height/2) + 1] = 1

    if option == "white-edge":
        canvas = np.pad(canvas, pad_width=1, mode='constant', constant_values=1)
        temp = np.zeros(3)
        for x in np.arange(0, height - 1):
            for y in np.arange(1, width+2):
                temp[0] = canvas[x][y-1]
                temp[1] = canvas[x][y]
                temp[2] = canvas[x][y + 1]
                for z in range(8):
                    if np.array_equal(bin_pat[z], temp):
                        canvas[x + 1, y] = bin_rep[z]
        return canvas

    if option == 'periodic':
        temp = np.zeros(3)
        for x in np.arange(0, height - 1):
            for y in np.arange(0, width+2):
                #print(canvas[x][y-1])
                temp[0] = canvas[x][y-1]
                temp[1] = canvas[x][y]
                if y == width+1:
                    temp[2] = canvas[x][0]
                else:
                    temp[2] = canvas[x][y + 1]

                for z in range(8):
                    if np.array_equal(bin_pat[z], temp):
                        canvas[x + 1, y] = bin_rep[z]
        return canvas

    temp = np.zeros(3)
    for x in np.arange(0, height - 1):
        for y in np.arange(0, width):
            temp[0] = canvas[x][y]
            temp[1] = canvas[x][y + 1]
            temp[2] = canvas[x][y + 2]
            for z in range(8):
                if np.array_equal(bin_pat[z], temp):
                    canvas[x + 1, y + 1] = bin_rep[z]
    return canvas


def game_of_life(size, grid):
    data = np.copy(grid)
    for x in np.arange(1, size[0] - 1):
        for y in np.arange(1, size[1] - 1):
            s = get_sum_game(grid, x, y)
            #kill
            if data[x][y] == 1:
                if s > 3: data[x][y] = 0
                if s < 2: data[x][y] = 0
            #revive
            elif data[x][y] == 0:
                if s == 3: data[x][y] = 1
    return data


def game_of_life_periodic(size, grid):
    data = np.copy(grid)
    for x in np.arange(0, size[0]):
        for y in np.arange(0, size[1]):
            s = get_sum_game_periodic(size,grid, x, y)
            # kill
            if data[x][y] == 1:
                if s > 3: data[x][y] = 0
                if s < 2: data[x][y] = 0
            # revive
            elif data[x][y] == 0:
                if s == 3: data[x][y] = 1
    return data


def get_sum_game_periodic(size, data, i, j):
    s = (data[(i - 1) % size[0]][(j - 1) % size[1]]) + (data[i % size[0]][(j - 1) % size[1]]) + (data[(i + 1) % size[0]][(j - 1) % size[1]]) + \
        (data[(i - 1) % size[0]][ j % size[1]])                        +                        (data[(i + 1) % size[0]][ j % size[1]])      + \
        (data[(i - 1) % size[0]][(j + 1) % size[1]]) + (data[i % size[0]][(j + 1) % size[1]]) + (data[(i + 1) % size[0]][(j + 1) % size[1]])
    return s


def get_sum_game(data, i, j):
    s = (data[i - 1][j - 1]) + (data[i][j - 1]) + (data[i + 1][j - 1]) + \
        (data[i - 1][j])             +            (data[i + 1][j])     + \
        (data[i - 1][j + 1]) + (data[i][j + 1]) + (data[i + 1][j + 1])
    return s


def create_animation(size, grid, frames):
    tensor = []
    tensor.append(grid)
    for i in range(frames):
        grid = game_of_life_periodic(size, grid)
        tensor.append(grid)
    return tensor


def binarize(data, threshold):
    binary = (data > threshold) * 255
    return binary


## type: 1-water, 2-forest
## state: 1-alive, 2-burning, 0-burnt
## wind: n, s, e, w
class cell:
    def __init__(self, type, state, iterator, RGB, ignition_factor):
        self.type = type
        self.state = state
        self.iterator = iterator
        self.RGB = RGB
        self.ignition_factor = ignition_factor


def get_forest(data):
    data = binarize(data, 100)
    shape = data.shape
    arr = np.empty((shape[0], shape[1]), dtype=object)
    for i in range(shape[0]):
        for j in range(shape[1]):
            if data[i][j] > 0:
                arr[i][j] = cell(2, 1, 0, [2, 69, 37], 0)  # forest
            else:
                arr[i][j] = cell(1, 0, 0, [7, 236, 240], 0)  # water
    return arr


def map_to_picture(data):
    shape = data.shape
    arr = np.ndarray((shape[0], shape[1], 3), dtype='uint8')
    for i in range(shape[0]):
        for j in range(shape[1]):
            arr[i][j] = data[i][j].RGB
    return arr


burning = ([255, 213, 97], [255, 51, 5])


def forest_fire_even(data,image, wind, humidity):
    global burning
    shape = data.shape
    for i in range(shape[0] - 1, 1):
        for j in range(shape[1] - 1, 1):
            cell = data[i][j]
            if cell.type != 1:
                # if its burning add 1 to iterator, select one from 2 colors and check the neighbourhood
                if cell.state == 2:
                    cell.iterator += 1
                    cell.RGB = burning[cell.iterator % 2]
                    # burned out
                    if cell.iterator > 4:
                        cell.state = 0
                        cell.RGB = [0, 0, 0]
                        cell.iterator = 0
                        cell.ignition_factor = 0

                # if its burnt add 1 to iterator
                if cell.state == 0 and cell.type == 2 :
                    cell.iterator += 1
                    # try to revive after 5 iterations
                    if cell.iterator > 170:
                        cell.state = np.random.choice([1, 0], 1, p=[1 /100, 99/ 100])  # 50% probability of reviving
                        if cell.state == 1:
                            cell.iterator = 0
                            cell.ignition_factor = 0
                            cell.RGB = [0, 255, 132]

                # if its normal
                if cell.state == 1:
                    # get sum and if sum > 0 ignite with weighted probability of success
                    s = chance_of_ignition(data, i, j)
                    if s>0:
                        if humidity < 5:
                            humidity = 6
                        else: s /= ((humidity + 1) / 10)

                        s += fire_location(data, i, j, wind)

                    if s > 0 and s < 5:
                        s = np.random.choice([1, 2], 1, p=[(7 - s) / 7, s / 7])
                        cell.state = s
                        cell.ignition_factor = s - 1

                    elif s > 5:
                        cell.state = 2

    return data, image


def forest_fire_odd(data,image, wind, humidity):
    global burning
    shape = data.shape
    for i in range(328, 1, -1):
        for j in range(598, 1, -1):
            cell = data[i][j]
            if cell.type != 1:
                # if its burning add 1 to iterator, select one from 2 colors and check the neighbourhood
                if cell.state == 2:
                    cell.iterator += 1
                    cell.RGB = burning[cell.iterator % 2]
                    # burned out
                    if cell.iterator > 4:
                        cell.state = 0
                        cell.RGB = [0, 0, 0]
                        cell.iterator = 0
                        cell.ignition_factor = 0

                # if its burnt add 1 to iterator
                if cell.state == 0 and cell.type == 2:
                    cell.iterator += 1
                    # try to revive after 5 iterations
                    if cell.iterator > 170:
                        cell.state = np.random.choice([1, 0], 1, p=[1 / 100, 99 / 100])  # 50% probability of reviving
                        if cell.state == 1:
                            cell.iterator = 0
                            cell.ignition_factor = 0
                            cell.RGB = [0, 255, 132]

                # if its normal
                if cell.state == 1:
                    # get sum and if sum > 0 ignite with weighted probability of success
                    s = chance_of_ignition(data, i, j)
                    if s>0:
                        if humidity <= 5:
                            humidity = 6
                        else: s /= ((humidity + 1) / 10)

                        s += fire_location(data, i, j, wind)

                    if s > 0 and s < 5:
                        s = np.random.choice([1, 2], 1, p=[(7 - s) / 7, s / 7])
                        cell.state = s
                        cell.ignition_factor = s - 1

                    elif s > 5:
                        cell.state = 2

                image[i][j] = cell.RGB
    return data, image


def chance_of_ignition(data, i, j):

    s = (data[i - 1][j - 1].ignition_factor) + (data[i][j - 1].ignition_factor) + (data[i + 1][j - 1].ignition_factor) + \
        (data[i - 1][j].ignition_factor) + (data[i + 1][j].ignition_factor) + \
        (data[i - 1][j + 1].ignition_factor) + (data[i][j + 1].ignition_factor) + (data[i + 1][j + 1].ignition_factor)


    return int(s)


def fire_location(data, i ,j, wind):
    s = 0
    #right
    if (data[i][j+1].ignition_factor) == 1:
        if wind == 'e':
            s += 5
        return s
    #above
    if (data[i-1][j].ignition_factor) == 1:
        if wind == 'n':
            s += 5
        return s
    if (data[i][j-1].ignition_factor) == 1:
        if wind == 'w':
            s += 5
        return s
    #below
    if (data[i+1][j].ignition_factor) == 1:
        if wind == 's':
            s += 5
        return s
    return s


# def create_forestFire_animation(grid, frames):
#     tensor = []
#     tensor.append(grid)
#     for i in range(frames):
#         tensor.append(map_to_picture(forest_fire(grid)))
#     return tensor

