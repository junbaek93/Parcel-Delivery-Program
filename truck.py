class Truck:
    def __init__(self, packages, speed, currentAddress):
        self.packages = packages
        self.speed = speed
        self.currentMilesDriven = 0
        self.currentAddress = currentAddress
        self.capacity = 0
        self.departure_time = None
        self.return_time = None

    def __str__(self):
        return "%s, %s, %s, %s, %s, %s, %s" % (
            self.packages, self.speed, self.currentMilesDriven, self.currentAddress,
            self.capacity, self.departure_time, self.return_time)
