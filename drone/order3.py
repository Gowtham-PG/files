import itertools
import json
import math


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the distance between two latitude-longitude coordinates using the Haversine formula.
    """
    radius = 6371  # Radius of the Earth in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c

    return distance


def tsp(coordinates):
    """
    Solves the Traveling Salesman Problem (TSP) and returns the optimal path and total distance.
    """
    num_points = len(coordinates)
    all_distances = {}

    # Calculate the distance between each pair of coordinates
    for i in range(num_points):
        for j in range(num_points):
            if i != j:
                dist = calculate_distance(coordinates[i][0], coordinates[i][1], coordinates[j][0], coordinates[j][1])
                all_distances[i, j] = dist

    # Initialize variables
    shortest_distance = float('inf')
    optimal_path = None

    # Find the optimal path using permutations
    for permutation in itertools.permutations(range(num_points)):
        distance = 0
        for i in range(num_points - 1):
            distance += all_distances[permutation[i], permutation[i + 1]]

        if distance < shortest_distance:
            shortest_distance = distance
            optimal_path = permutation

    return optimal_path, shortest_distance


# Read coordinates from the JSON file
with open('waypoint3.json', 'r') as file:
    data = json.load(file)
    waypoint_data = data['waypoints']

# Add the given latitude, longitude, and altitude as the starting and ending points
start_lat = 26.98991082
start_lon = 80.8821201
end_lat = 26.9885441
end_lon = 80.8923233

# Add altitude = 20 to each waypoint
waypoint_data_with_altitude = []
for i, waypoint in enumerate(waypoint_data):
    waypoint_with_altitude = {
        "latitude": waypoint['latitude'],
        "longitude": waypoint['longitude'],
        "altitude": 20 if i != 0 and i != len(waypoint_data) - 1 else None
    }
    waypoint_data_with_altitude.append(waypoint_with_altitude)

coordinates = [(start_lat, start_lon)] + [(waypoint['latitude'], waypoint['longitude']) for waypoint in waypoint_data_with_altitude] + [(end_lat, end_lon)]

optimal_path, shortest_distance = tsp(coordinates)

# Create a new dictionary to store the latitude, longitude, and altitude of the optimal path
optimal_path_coordinates = {"waypoints": []}
for index in optimal_path:
    lat, lon = coordinates[index]
    if index != 0 and index != len(coordinates) - 1:
        optimal_path_coordinates["waypoints"].append({"latitude": lat, "longitude": lon, "altitude": 20})

# Save the optimal path coordinates to a JSON file
with open('optimal_path3.json', 'w') as file:
    json.dump(optimal_path_coordinates, file, indent=2)

print("Optimal Path and shortest distance saved in optimal_path.json")
