class Package:
    def __init__(self, packageID, address, deadline, city, zipcode, weight, status, notes):
        self.packageID = packageID
        self.address = address
        self.deadline = deadline
        self.city = city
        self.zipcode = zipcode
        self.weight = weight
        self.status = status
        self.notes = notes
        self.time = None
        self.packageDepartureTime = None
        self.deliverTime = None

    def __str__(self):
        return "%s, %s, %s, %s, %s, %s" % (
            self.address, self.deadline, self.city,  self.zipcode, self.weight, self.status)

    def getStatusByTime(self, searchByTime):
        if self.packageDepartureTime <= searchByTime < self.deliverTime:
            return "EN_ROUTE"
        elif searchByTime >= self.deliverTime:
            return "DELIVERED"
        else:
            return "AT_THE_HUB"

