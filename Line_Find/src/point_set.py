class PointSet:

    def __init__(self, points):
        self.points = points
        self.points_d = {}
        self.size = len(points)

        # Init points in point dictionary
        for p in points:
            self.points_d[p] = None

    def print_points(self):
        print(self.points)
