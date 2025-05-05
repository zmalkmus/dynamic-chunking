import math

class Shape:
    def __init__(self, path):
        self.path = path

class Circle(Shape):
    def __init__(self, path, radius):
        super().__init__(path)
        self.r = radius
        self.r2 = radius * radius

    # ------------------------------------------------------------------ API
    def circumference(self):
        return 2 * math.pi * self.r

    def area(self):
        return math.pi * self.r * self.r

    def border_crosses(self, timestep, block, eps=1e-12) -> bool:
        """
        True  → circumference intersects the block (touches interior).
        False → circle fully outside OR fully contains the block.
        """
        cx = self.path[timestep][0]
        cy = self.path[timestep][1]

        # closest point on rectangle to circle centre
        nx = min(max(cx, block.xmin), block.xmax)
        ny = min(max(cy, block.ymin), block.ymax)
        dmin2 = (cx - nx) ** 2 + (cy - ny) ** 2

        # farthest rectangle corner from circle centre
        corners = (
            (block.xmin, block.ymin),
            (block.xmin, block.ymax),
            (block.xmax, block.ymin),
            (block.xmax, block.ymax),
        )
        dmax2 = max((cx - x) ** 2 + (cy - y) ** 2 for x, y in corners)

        return dmin2 <= self.r2 + eps and dmax2 >= self.r2 - eps
    
    def center(self, timestep):
        return self.path[timestep]