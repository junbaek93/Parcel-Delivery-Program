
import csv
import package
import truck
from datetime import timedelta
from package import Package
from hashTable import HashTable

# GLOBAL VARIABLES
HUB_ADDRESS = "4001 South 700 East"


# Loads package data from package.csv into a package hash table
def load_package_file(fileName):
    with open(fileName) as packageFile:
        packageData = csv.reader(packageFile)
        for packages in packageData:
            packageID = int(packages[0])
            address = packages[1]
            deadline = packages[5]
            city = packages[2]
            zipcode = packages[4]
            weight = packages[6]
            status = "AT_THE_HUB"
            notes = packages[7]

            # Create a class package object to be inputted into the hash table
            packages = Package(
                packageID, address, deadline, city, zipcode, weight, status, notes
            )

            # inserts package data into the hash table with the package ID as the key
            packageHashTable.insert(packageID, packages)


# Loads distance data matrix from distance.csv into a 2 dimension matrix list
def load_distance_file(fileName):
    with open(fileName) as distanceFile:
        distanceData = csv.reader(distanceFile, delimiter=",")
        for distance in distanceData:
            distanceMatrix.append(distance)
    # The distance CSV matrix is bidirectional. Distance between x to y is the same as y to x.
    for x_value in range(len(distanceMatrix)):
        for y_value in range(len(distanceMatrix)):
            if distanceMatrix[x_value][y_value] == "":
                distanceMatrix[x_value][y_value] = distanceMatrix[y_value][x_value]


# loads address data from address.csv into an address list
def load_address_file(fileName):
    with open(fileName) as addressFile:
        addressData = csv.reader(addressFile, delimiter=",")
        for address in addressData:
            addressList.append(address)


# Searches the distance between two locations within the distance matrix
def distance_between_addresses(address1, address2):
    for location in addressList:
        if address1 in location:
            x_value = location[0]
        if address2 in location:
            y_value = location[0]
    return distanceMatrix[int(x_value)][int(y_value)]


# convert distance to time
def distance_to_time(distance):
    time = distance / 18
    hour = (time * 60) / 60
    minute = (hour * 60) % 60
    second = (minute * 60) % 60

    return timedelta(hours=int(hour), minutes=int(minute), seconds=round(second))


# Nearest Neighbor Algorithm, finding the nearest location between a location and a set of package addresses
def find_nearest_location(address, truckPackages):
    closestLocationID = None
    minDistance = 999
    for packageID in truckPackages:
        currentPackage = packageHashTable.search(packageID)
        packageDistance = float(
            distance_between_addresses(
                address, currentPackage.address
            )
        )
        if packageDistance < minDistance:
            minDistance = packageDistance
            closestLocationID = packageID
    return closestLocationID


# Nearest Neighbor Algorithm, finding the nearest location between two sets of package address
def find_nearest_between_two_list(packageList, truckPackages):
    closestLocationID = 0
    minDistance = 999
    for truckPackageID in truckPackages:
        truckPackage = packageHashTable.search(truckPackageID)
        for packageListID in packageList:
            currentPackage = packageHashTable.search(packageListID)
            packageDistance = float(
                distance_between_addresses(
                    truckPackage.address,
                    currentPackage.address,
                )
            )
            if packageDistance < minDistance:
                minDistance = packageDistance
                closestLocationID = packageListID
    return closestLocationID


# Load the rest of the package to the truck
def load_packages():
    packageList = []  # list of packages that are not loaded onto a truck
    priorityList1 = []  # list of packages that have a deadline of 10:30AM
    priorityList2 = []  # list of packages that are delayed with a 10:30AM deadline

    for i in range(1, 41):
        currentPackage = packageHashTable.search(i)
        if any(x == i for x in truck1.packages):
            continue
        elif any(x == i for x in truck2.packages):
            continue
        elif any(x == i for x in truck3.packages):
            continue
        elif currentPackage.notes == "Delayed on flight---will not arrive to depot until 9:05 am":
            priorityList2.append(i)
        elif currentPackage.deadline == "10:30 AM":
            priorityList1.append(i)
        else:
            packageList.append(i)

    # Load packages that are delayed and will not be able to depart until 9:05AM onto truck 3.
    # Truck 3 is set to depart at 9:05AM
    truck3.packages = priorityList2

    # Nearest neighbor algorithm between two sets of points (set of truck packages and set of ready to load packages).
    # The algorithm finds the shortest distance between two points, then it will load the truck with the shortest
    # distance relative to the truck and the set of packages.

    # Nearest X is the packages within the truck.
    # Nearest Y is the set of packages ready to load.
    while len(priorityList1) != 0:
        truck1NearestX = packageHashTable.search(
            find_nearest_between_two_list(truck1.packages, priorityList1))
        truck1NearestY = packageHashTable.search(
            find_nearest_between_two_list(priorityList1, truck1.packages))
        truck3NearestX = packageHashTable.search(
            find_nearest_between_two_list(truck3.packages, priorityList1))
        truck3NearestY = packageHashTable.search(
            find_nearest_between_two_list(priorityList1, truck3.packages))
        if distance_between_addresses(truck1NearestX.address, truck1NearestY.address) \
                >= distance_between_addresses(truck3NearestX.address, truck3NearestY.address):
            truck1.packages.append(truck1NearestY.packageID)
            priorityList1.remove(truck1NearestY.packageID)
        else:
            truck3.packages.append(truck3NearestY.packageID)
            priorityList1.remove(truck3NearestY.packageID)

    # Load packages that are closest to truck 1 packages with a max capacity of 16 packages.
    # Truck 1 must return to the hub ASAP so the next truck can deploy
    while len(truck1.packages) < 16:
        nearest_location = find_nearest_between_two_list(packageList, truck1.packages)
        truck1.packages.append(nearest_location)
        packageList.remove(nearest_location)

    # Uses the same algorithm as the one above, but once a truck loads max capacity, the other truck will
    # receive the rest of the packages that are ready to load.
    while len(packageList) != 0:
        if len(truck2.packages) == 16:
            truck3.packages.extend(packageList)
            break
        if len(truck3.packages) == 16:
            truck2.packages.extend(packageList)
            break
        truck2NearestX = packageHashTable.search(
            find_nearest_between_two_list(packageList, truck2.packages))
        truck2NearestY = packageHashTable.search(
            find_nearest_between_two_list(truck2.packages, packageList))
        truck3NearestY = packageHashTable.search(
            find_nearest_between_two_list(packageList, truck3.packages))
        truck3NearestX = packageHashTable.search(
            find_nearest_between_two_list(truck3.packages, packageList))
        if distance_between_addresses(truck2NearestX.address, truck2NearestY.address) \
                >= distance_between_addresses(truck3NearestY.address, truck3NearestX.address):
            truck2.packages.append(truck2NearestX.packageID)
            packageList.remove(truck2NearestX.packageID)
        else:
            truck3.packages.append(truck3NearestY.packageID)
            packageList.remove(truck3NearestY.packageID)


# Deliver packages within the truck. The packages in the truck are reorganized by nearest neighbor
def deliver_packages(truckData):
    packagesDelivered = []  # Organizes the packages delivered by nearest neighbor.

    while len(truckData.packages) != 0:
        # initialize nearestLocation using utilizing nearest neighbor algorithm to deliver the packages
        # currentPackage is a package that is set to be delivered
        nearestLocation = find_nearest_location(truckData.currentAddress, truckData.packages)
        currentPackage = packageHashTable.search(nearestLocation)

        # Sets the package departure time to the departure time of the truck
        currentPackage.packageDepartureTime = truckData.departure_time

        # Adds package to the packageDeliveredList that will eventually replace the packages in the truck object
        packagesDelivered.append(nearestLocation)

        # Add truck miles based on the current location of the truck and the nearest location
        truckData.currentMilesDriven += float(
            distance_between_addresses(
                truckData.currentAddress,
                currentPackage.address,
            )
        )

        # Sets the current address to the nearest location
        truckData.currentAddress = currentPackage.address

        # Removes the nearest neighbor package within the truck object
        truckData.packages.remove(
            find_nearest_location(truckData.currentAddress, truckData.packages)
        )

        # Changes the status of the package to DELIVERED
        currentPackage.status = "DELIVERED"

        # Sets the time elapsed to deliver the package by converting the truck distance into time
        currentPackage.time = distance_to_time(truckData.currentMilesDriven)

        # Sets the package deliver time
        currentPackage.deliverTime = currentPackage.time + truckData.departure_time

    # Sets the total amount the truck have driven
    truckData.currentMilesDriven += float(
        distance_between_addresses(truckData.currentAddress, HUB_ADDRESS)
    )

    # Sets the time the truck returns to the hub
    truckFinalTime = packageHashTable.search(packagesDelivered[len(packagesDelivered) - 1])
    truckData.return_time = distance_to_time(
        float(distance_between_addresses(truckData.currentAddress, HUB_ADDRESS))
    ) + truckFinalTime.deliverTime

    # Sets the packaged that was delivered in order back into truck packages
    truckData.packages = packagesDelivered


# initialize classes
packageHashTable = HashTable()
load_package_file("csv/package.csv")

distanceMatrix = []
load_distance_file("csv/distance.csv")

addressList = []
load_address_file("csv/address.csv")

# preset packages based on certain criteria.
# Package set 1: Packages that must be grouped together
# Package set 2: Packages that must be in truck 2
packageSet1 = [13, 14, 15, 16, 19, 20]
packageSet2 = [3, 18, 36, 38, 17, 9]
packageSet3 = []

# Initialize Truck classes
# Truck 1: First truck to leave the hub. Must carry the earliest delivery deadlines
# Truck 2: Last to leave the hub. Carries the wrong listed address that will be updated at 10:20AM
# Truck 3: Second to leave the hub. Carries delayed packages that do not arrive at the hub until 09:05AM
truck1 = truck.Truck(packageSet1, 18, HUB_ADDRESS)
truck1.departure_time = timedelta(hours=8, minutes=0, seconds=0)

truck2 = truck.Truck(packageSet2, 18, HUB_ADDRESS)
truck2.departure_time = timedelta(hours=10, minutes=20, seconds=0)

truck3 = truck.Truck(packageSet3, 18, HUB_ADDRESS)
truck3.departure_time = timedelta(hours=9, minutes=5, seconds=0)

load_packages()


# PRINTS ALL PACKAGES IN THE HASH TABLE
def print_all_package_info():
    for index in range(1, 41):
        currentPackage = packageHashTable.search(index)
        packageID = currentPackage.packageID
        location = (
                currentPackage.address
                + " "
                + currentPackage.city
                + ", "
                + currentPackage.zipcode
        )
        deadline = currentPackage.deadline
        status = currentPackage.status
        weight = currentPackage.weight
        time = str(currentPackage.time + currentPackage.packageDepartureTime)
        notes = currentPackage.notes

        print(f"{'ID:': <4}{packageID : <5}", end="")
        if status == "DELIVERED":
            print(
                f"{'STATUS:': <9}{Colors.GREEN + status + Colors.ENDC : <22}"
                f"{time: <12}",
                end="",
            )
        if status == "EN_ROUTE":
            print(
                f"{'STATUS:': <9}{Colors.YELLOW + status + Colors.ENDC : <34}", end=""
            )
        if status == "AT_THE_HUB":
            print(f"{'STATUS:': <9}{Colors.RED + status + Colors.ENDC : <34}", end="")
        print(
            f"{'DELIVER TO:': <12}{location: <70}"
            f"{'WEIGHT:' : <9}{weight: <10}"
            f"{'DEADLINE:' : <9}{deadline: <20}"
            f"{'NOTES:' : <9}{notes: <20}"
        )
    print()


# PRINTS PACKAGES BY PACKAGE ID, ADDRESS, CITY, or, ZIPCODE
def print_by_package_component(index):
    currentPackage = packageHashTable.search(index)
    address = currentPackage.address
    deadline = currentPackage.deadline
    city = currentPackage.city
    zipCode = currentPackage.zipcode
    status = currentPackage.status
    time = str(currentPackage.time + currentPackage.packageDepartureTime)

    print(
        f"{'ADDRESS: '}{address}\n"
        f"{'DEADLINE: '}{deadline}\n"
        f"{'CITY: '}{city}\n"
        f"{'ZIPCODE: '}{zipCode}\n"
        f"{'STATUS: '}{Colors.GREEN + status + Colors.ENDC}{' @ '}{time}\n"
    )


# PRINTS ALL PACKAGE INFO FOR EACH TRUCK
def print_truck_package_info(truckData):
    for index in truckData.packages:
        currentPackage = packageHashTable.search(index)
        packageID = currentPackage.packageID
        location = (
                currentPackage.address
                + " "
                + currentPackage.city
                + ", "
                + currentPackage.zipcode
        )
        deadline = currentPackage.deadline
        status = currentPackage.status
        weight = currentPackage.weight
        time = str(currentPackage.time + truckData.departure_time)
        notes = currentPackage.notes

        print(f"{'ID:': <4}{packageID : <5}", end="")
        if status == "DELIVERED":
            print(
                f"{'STATUS:': <9}{Colors.GREEN + status + Colors.ENDC : <22}"
                f"{time: <12}",
                end="",
            )
        if status == "EN_ROUTE":
            print(
                f"{'STATUS:': <9}{Colors.YELLOW + status + Colors.ENDC : <34}", end=""
            )
        if status == "AT_THE_HUB":
            print(f"{'STATUS:': <9}{Colors.RED + status + Colors.ENDC : <34}", end="")
        print(
            f"{'DELIVER TO:': <12}{location: <70}"
            f"{'WEIGHT:' : <9}{weight: <10}"
            f"{'DEADLINE:' : <9}{deadline: <20}"
            f"{'NOTES:' : <9}{notes: <20}"
        )
    print("\n\n")


# SEARCHES AND PRINTS ALL PACKAGES IN A SPECIFIC TIME
def print_all_package_info_by_specific_time(specificTime):
    for index in range(1, 41):
        currentPackage = packageHashTable.search(index)
        packageID = currentPackage.packageID
        location = (
                currentPackage.address
                + " "
                + currentPackage.city
                + ", "
                + currentPackage.zipcode
        )
        status = package.Package.getStatusByTime(currentPackage, specificTime)
        deadline = currentPackage.deadline
        weight = currentPackage.weight
        deliverTime = str(currentPackage.deliverTime)
        notes = currentPackage.notes

        print(f"{'ID:': <4}{packageID : <5}", end="")
        if status == "DELIVERED":
            print(
                f"{'STATUS:': <9}{Colors.GREEN + status + Colors.ENDC : <22}"
                f"{deliverTime: <12}",
                end="",
            )
        if status == "EN_ROUTE":
            print(
                f"{'STATUS:': <9}{Colors.YELLOW + status + Colors.ENDC : <34}", end=""
            )
        if status == "AT_THE_HUB":
            print(f"{'STATUS:': <9}{Colors.RED + status + Colors.ENDC : <34}", end="")
        print(
            f"{'DELIVER TO:': <12}{location: <70}"
            f"{'WEIGHT:' : <9}{weight: <10}"
            f"{'DEADLINE:' : <9}{deadline: <20}"
            f"{'NOTES:' : <9}{notes: <20}"
        )


# SEARCHES AND PRINTS EACH TRUCK PACKAGES IN A SPECIFIC TIME
def print_truck_package_info_by_specific_time(truckData, specificTime):
    totalMiles = 0
    totalTime = timedelta(hours=0, minutes=0, seconds=0)
    deliveredInfoList = []
    checkAllPackageStatus = []
    for index in truckData.packages:
        currentPackage = packageHashTable.search(index)
        packageID = currentPackage.packageID
        location = (
                currentPackage.address
                + " "
                + currentPackage.city
                + ", "
                + currentPackage.zipcode
        )
        deadline = currentPackage.deadline
        status = package.Package.getStatusByTime(currentPackage, specificTime)
        weight = currentPackage.weight
        DeliverTime = str(currentPackage.deliverTime)
        notes = currentPackage.notes

        print(f"{'ID:': <4}{packageID : <5}", end="")
        if status == "DELIVERED":
            deliveredInfoList.append(index)
            checkAllPackageStatus.append("DELIVERED")
            print(
                f"{'STATUS:': <9}{Colors.GREEN + status + Colors.ENDC : <22}"
                f"{DeliverTime: <12}",
                end="",
            )
        if status == "EN_ROUTE":
            checkAllPackageStatus.append("EN_ROUTE")
            print(f"{'STATUS:': <9}{Colors.YELLOW + status + Colors.ENDC : <34}", end="")
        if status == "AT_THE_HUB":
            checkAllPackageStatus.append("AT_THE_HUB")
            print(f"{'STATUS:': <9}{Colors.RED + status + Colors.ENDC : <34}", end="")
        print(
            f"{'DELIVER TO:': <12}{location: <70}"
            f"{'WEIGHT:' : <9}{weight: <10}"
            f"{'DEADLINE:' : <9}{deadline: <20}"
            f"{'NOTES:' : <9}{notes: <20}"
        )
    currentLocation = HUB_ADDRESS
    for packageID in deliveredInfoList:
        nextLocation = packageHashTable.search(packageID).address
        totalMiles += float(distance_between_addresses(currentLocation, nextLocation))
        totalTime += distance_to_time(float(distance_between_addresses(currentLocation, nextLocation)))
        currentLocation = nextLocation
    if all(x == "DELIVERED" for x in checkAllPackageStatus):
        if truckData.return_time > specificTime:
            print(f"\n{Colors.YELLOW + 'RETURNING TO HUB'}{Colors.ENDC}")
        else:
            totalMiles += float(distance_between_addresses(currentLocation, HUB_ADDRESS))
            totalTime += distance_to_time(float(distance_between_addresses(currentLocation, HUB_ADDRESS)))
            print(f"\n{Colors.GREEN + 'RETURNED TO HUB AT: '}{truckData.departure_time + totalTime}{Colors.ENDC}")
    if all(x == "AT_THE_HUB" for x in checkAllPackageStatus):
        print(f"\n{Colors.RED + 'READY TO DEPART AT '}{truckData.departure_time}{Colors.ENDC}")
    if any(x == "EN_ROUTE" for x in checkAllPackageStatus):
        print(f"\n{Colors.YELLOW + 'CURRENTLY DELIVERING PACKAGES' + Colors.ENDC}")
    print("Miles Driven:", "%.2f" % totalMiles, "\nTime Driven:", totalTime)


# Prints all truck milage
def print_truck_milage(truckData):
    print(
        "============================================\n" "Miles: ",
        truckData.currentMilesDriven,
        "\n============================================\n",
    )


# Prints all truck time
def print_truck_time(truckData):
    print(
        "============================================\n" "Total Time: ",
        truckData.return_time - truckData.departure_time,
        "\n============================================\n",
    )


# Preset colors for UI visibility
class Colors:
    RED = "\033[31m"  # "AT_THE_HUB"
    ENDC = "\033[m"  # return to original color
    GREEN = "\033[32m"  # "DELIVERED"
    YELLOW = "\033[33m"  # "EN_ROUTE


# Initiate UI
class Main:
    run_menu = True
    while run_menu:

        # Once the program starts, the system will print out each truck by departure time.
        userInput = input("Start the program? (Y/N):")
        if userInput == "Y" or userInput == "y":

            deliver_packages(truck1)
            print(
                "\nTruck 1 departed at",
                truck1.departure_time,
                ", returned at",
                truck1.return_time,
            )
            print_truck_package_info(truck1)

            deliver_packages(truck3)
            print(
                "\nTruck 3 departed at",
                truck3.departure_time,
                ", returned at",
                truck3.return_time,
            )
            print_truck_package_info(truck3)

            deliver_packages(truck2)
            print(
                "\nTruck 2 departed at",
                truck2.departure_time,
                ", returned at",
                truck2.return_time,
            )
            print_truck_package_info(truck2)

            run_menu = False
        elif userInput == "N" or userInput == "n":
            exit()
        else:
            print(
                "\n",
                Colors.YELLOW
                + "ERROR! INVALID INPUT! PLEASE SELECT FROM THE OPTIONS"
                + Colors.ENDC,
                "\n",
            )

    # The main menu of the UI.
    repeat_Main_Menu = True
    while repeat_Main_Menu:
        print(
            "\nMAIN MENU: \n"
            "1. View Packages\n"
            "2. View Miles\n"
            "3. View Time\n"
            "4. Exit"
        )
        userInput = input("SELECT OPTION: ")

        # The package menu will let the user search by ID, Address, city, or zipcode.
        if userInput == "1":
            print_all_package_info()
            repeat_Package_Lookup_Menu = True
            while repeat_Package_Lookup_Menu:
                print(
                    "\nPACKAGE LOOKUP MENU:\n"
                    "1. Search by ID\n"
                    "2. Search by Address\n"
                    "3. Search by City\n"
                    "4. Search by Zipcode\n"
                    "5. Return to Package Menu\n"
                )
                userPackageLookupMenu = input("SELECT OPTION: ")

                if userPackageLookupMenu == "1":
                    searchByID = input("\nPlease enter package ID: ")
                    foundLookup = 0
                    for index in range(1, 41):
                        if packageHashTable.search(index).packageID == int(searchByID):
                            print_by_package_component(index)
                            foundLookup = 1
                    if foundLookup == 0:
                        print("Package ID not found. Please try again")

                if userPackageLookupMenu == "2":
                    searchByAddress = input("\nPlease enter Address: ")
                    foundLookup = 0
                    for index in range(1, 41):
                        if packageHashTable.search(index).address == searchByAddress:
                            print_by_package_component(index)
                            foundLookup = 1
                    if foundLookup == 0:
                        print("Package address not found. Please try again")

                if userPackageLookupMenu == "3":
                    searchByCity = input("\nPlease enter a city: ")
                    foundLookup = 0
                    for index in range(1, 41):
                        if packageHashTable.search(index).city == searchByCity:
                            print_by_package_component(index)
                            foundLookup = 1
                    if foundLookup == 0:
                        print("Package city not found. Please try again")

                if userPackageLookupMenu == "4":
                    searchByZipcode = input("\nPlease enter a Zipcode: ")
                    foundLookup = 0
                    for index in range(1, 41):
                        if packageHashTable.search(index).zipcode == searchByZipcode:
                            print_by_package_component(index)
                            foundLookup = 1
                    if foundLookup == 0:
                        print("Package Zipcode not found. Please try again")
                if userPackageLookupMenu == "5":
                    repeat_Package_Lookup_Menu = False

        # prints out the milage for each truck
        elif userInput == "2":
            print("\nTruck 1:")
            print_truck_milage(truck1)

            print("Truck 2:")
            print_truck_milage(truck2)

            print("Truck 3:")
            print_truck_milage(truck3)

            print(
                "Total Miles:",
                float(truck1.currentMilesDriven)
                + float(truck2.currentMilesDriven)
                + float(truck3.currentMilesDriven),
                )

        elif userInput == "3":
            print("\nTruck 1:")
            print_truck_time(truck1)

            print("Truck 2:")
            print_truck_time(truck2)

            print("Truck 3:")
            print_truck_time(truck3)

            print("Total Time:",
                  (truck1.return_time - truck1.departure_time)
                  + (truck2.return_time - truck2.departure_time)
                  + (truck3.return_time - truck3.departure_time)
                  )
            searchSpecificTime = input(
                "Please enter a specific time (HH:MM:SS): "
            )
            try:
                (hour, minute, second) = searchSpecificTime.split(":")
                searchSpecificTime_datetime = timedelta(
                    hours=int(hour), minutes=int(minute), seconds=int(second)
                )
                print("\nAll package info at", searchSpecificTime_datetime)
                print_all_package_info_by_specific_time(
                    searchSpecificTime_datetime
                )

                print("\nTruck 1 info at", searchSpecificTime_datetime)
                print_truck_package_info_by_specific_time(
                    truck1, searchSpecificTime_datetime
                )

                print("\nTruck 2 info at", searchSpecificTime_datetime)
                print_truck_package_info_by_specific_time(
                    truck2, searchSpecificTime_datetime
                )

                print("\nTruck 3 info at", searchSpecificTime_datetime)
                print_truck_package_info_by_specific_time(
                    truck3, searchSpecificTime_datetime
                )
            except:
                print("Please try again")

        # Exit the program
        elif userInput == "4":
            repeat_Main_Menu = False

        else:
            print(
                "\n",
                Colors.YELLOW
                + "ERROR! INVALID INPUT! PLEASE SELECT FROM THE OPTIONS"
                + Colors.ENDC,
                "\n",
            )
