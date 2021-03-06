import numpy as np


class Cell:
    def __init__(self, id, contour, cent, area, split_p = False,split_c=False):
        self.id = id
        self.contour = contour
        self.cent = cent
        self.area = area
        self.previous_positions = [cent]
        self.speed = 0
        self.total_dist = 0
        self.net_dist = 0
        self.confinement_ratio = 0
        ### check if cell is splitting, default value is false
        self.split_p = split_p  # parent
        self.split_c = split_c  # child


    def get_id(self):
        return self.id

    def get_centroid(self):
        return self.cent

    ### add area
    def get_area(self):
        return self.area

    def get_contour(self):
        return self.contour

    def if_split(self):
        return self.split_p or self.split_c

    def get_speed(self):
        return self.speed

    def get_confinement_ratio(self):
        return self.confinement_ratio

    def get_total_dist(self):
        return self.total_dist

    def get_net_dist(self):
        return self.net_dist

    def get_prev_positions(self):
        return self.previous_positions

    def update(self, contour, cent, area):
        # Save previous position
        self.previous_positions.append(cent)
        # Update key attributes
        self.contour = contour
        self.cent = cent
        self.area = area
        # Recalculate metrics
        self.update_speed()
        self.update_total_dist()
        self.update_net_dist()
        self.update_confinement_ratio()

    def update_speed(self):
        if len(self.previous_positions) > 1:
            self.speed = self.__distance__(self.previous_positions[-1], self.previous_positions[-2]) / 1  # pixels/frame

    def update_total_dist(self):
        self.total_dist += self.__distance__(self.previous_positions[-1], self.previous_positions[-2])

    def update_net_dist(self):
        self.net_dist = self.__distance__(self.previous_positions[0], self.previous_positions[-1])

    def update_confinement_ratio(self):
        if self.total_dist > 0 and self.net_dist > 0:
            self.confinement_ratio = self.total_dist / self.net_dist

    def __distance__(self, p1, p2):
        return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
