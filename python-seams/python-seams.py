import cv2
import numpy as np
try:
    from tqdm import tqdm
except:
    print("TQDM is not installed. No progress bars. Use this command to get them!")
    print("pip install tqdm")


def read_img(filename):
    " Read an image as a list of list of list of ints "
    img = cv2.imread(filename)
    return img.tolist()


def write_img(img, filename):
    " Write the list of list of list of ints to a file "
    cv2.imwrite(filename, np.array(img))


def square_diff(v1, v2):
    " Calculate the squared difference of two lists of ints "
    return (v2[0]-v1[0])**2 + (v2[1]-v1[1])**2 + (v2[2]-v1[2])**2
    # return sum((p2-p1) ** 2 for p1, p2 in zip(v1, v2))


def calculate_energy(img, x, y):
    " Calculate the energy at a given pixel in the image "
    width = len(img[0])
    height = len(img)
    x_left = x-1 if x else 0
    x_right = x+1 if x < width-1 else width-1
    y_up = y-1 if y else 0
    y_down = y+1 if y < height-1 else height-1
    x_diff = square_diff(img[y][x_left], img[y][x_right])
    y_diff = square_diff(img[y_up][x], img[y_down][x])
    return x_diff + y_diff


def print_array(items):
    " Quickly print out a list of list of values "
    print("\n".join(", ".join(map(str, row)) for row in items))


class Seams:
    " Class for doing seam carving "
    energies = [[int]]

    def __init__(self, data):
        self.data = data
        self.width = len(data[0])
        self.height = len(data)

    def setup_seams(self):
        " Put zeroes (or None) in the seams and backs lists of lists "
        self.seams = [[0]*self.width for y in range(self.height)]
        self.seams[0] = self.energies[0].copy()
        self.backs = [[None for i in self.energies[0]]]
        self.backs.extend([[0]*self.width for i in range(self.height-1)])

    def fill_seams(self):
        " Calculate the seams based on their energies, using Dynamic Programming "
        previous_row = self.energies[0]
        width = len(previous_row)
        for row_id in range(1, len(self.energies)):
            e, sm, b = self.energies[row_id], self.seams[row_id], self.backs[row_id]
            for column_id in range(width):
                min_loc, min_energy = column_id, previous_row[column_id]
                if column_id:
                    pe = previous_row[column_id-1]
                    if pe <= min_energy:
                        min_loc, min_energy = column_id-1, pe
                if column_id+1 < width-1:
                    pe = previous_row[column_id+1]
                    if pe < min_energy:
                        min_loc, min_energy = column_id+1, pe
                sm[column_id] += min_energy + e[column_id]
                b[column_id] = min_loc
            previous_row = e

    def backtrace_seam(self):
        " Iterate up from the bottom to find the minimal seam "
        column_id = self.seams[-1].index(min(self.seams[-1]))
        row_id = self.height-1
        path = []
        while column_id != None:
            path.append(column_id)
            column_id = self.backs[row_id][column_id]
            row_id -= 1
        return path[::-1]

    def find_lowest_energy_seam(self) -> [int]:
        " Find the lowest energy seam using dynamic programming "
        self.setup_seams()
        self.fill_seams()
        return self.backtrace_seam()

    def calculate_energies(self):
        " Update the energies of all pixels "
        self.energies = [[0]*self.width for _ in range(self.height)]
        for row_id, row_values in enumerate(self.data):
            for column_id, pixel in enumerate(row_values):
                pixel_energy = calculate_energy(self.data, column_id, row_id)
                self.energies[row_id][column_id] = pixel_energy

    def remove_lowest_seam(self):
        '''Removes a seam from the image'''
        column_ids = self.find_lowest_energy_seam()
        for column_id, row, energy in zip(column_ids, self.data, self.energies):
            row.pop(column_id)
            energy.pop(column_id)
        self.width -= 1
        return column_ids

    def update_energy(self, column_ids):
        " Only update the affected pixels. May not actually work, I'm tired. "
        for row_id, (row_values, column_id) in enumerate(zip(self.data, column_ids)):
            for i in [-1, 0, 1]:
                if column_id+i < 0:
                    continue
                if column_id+i >= self.width:
                    continue
                pixel_energy = calculate_energy(self.data, column_id+i, row_id)
                self.energies[row_id][column_id+i] += pixel_energy

    def scale_image(self, n):
        " Scale the image down "
        original_width = seams.width
        self.calculate_energies()
        for i in tqdm(range(n, original_width)):
            path = self.remove_lowest_seam()
            self.update_energy(path)


if __name__ == "__main__":
    # img = read_img("tower.jpg")
	img = read_img("landscape.jpg")
    # Simple test case for debugging.
    #BLACK, WHITE = [0, 0, 0], [1, 1, 1]
    #RED, BLUE = [1, 0, 0], [0, 0, 1]
    # img = [[WHITE, WHITE, WHITE, BLACK],
    #       [BLACK, BLUE, RED, WHITE],
    #       [WHITE, RED, WHITE, BLACK],
    #       [BLACK, WHITE, BLACK, WHITE]]
	
	seams = Seams(img)
	# seams.scale_image(700)  # int(seams.width*2/3))
	# seams.scale_image(960)
	seams.scale_image(1440)
	# write_img(seams.data, "saved.jpg")
	write_img(seams.data, "output25percent.jpg")
