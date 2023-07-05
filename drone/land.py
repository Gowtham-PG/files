#!/usr/bin/python3

import time
import argparse
import json
import math
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command

parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect', help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None

if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()

vehicle = connect(connection_string, wait_ready=True)

# Define get_distance_metres function
def get_distance_metres(aLocation1, aLocation2):
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

# 1) Arm and take off to an altitude of 10 meters
target_altitude = 10

print("Arming motors")
vehicle.mode = VehicleMode("GUIDED")
vehicle.armed = True

while not vehicle.armed:
    print(" Waiting for arming...")
    time.sleep(1)

print("Taking off!")
vehicle.simple_takeoff(target_altitude)

while True:
    print(" Altitude: ", vehicle.location.global_relative_frame.alt)
    if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
        print("Reached target altitude")
        break
    time.sleep(1)

# 2) Reach initial latitude and longitude and land
initial_lat = 26.9887067
initial_lon = 80.8985996
landing_altitude = 0.5  # Set the altitude for landing in meters

def reach_and_land(initial_lat, initial_lon, landing_altitude):
    target_location = LocationGlobalRelative(initial_lat, initial_lon, landing_altitude)

    print("Going to initial position")
    vehicle.simple_goto(target_location)

    while True:
        current_altitude = vehicle.location.global_relative_frame.alt
        distance_to_target = get_distance_metres(target_location, vehicle.location.global_relative_frame)
        print(" Altitude: ", current_altitude)
        print(" Distance to target: ", distance_to_target)

        if current_altitude <= landing_altitude and distance_to_target <= 1.0:
            print("Reached initial position")
            break
        time.sleep(1)

    print("Landing")
    vehicle.mode = VehicleMode("LAND")

    while vehicle.armed:
        print(" Waiting for disarming...")
        time.sleep(1)

    print("Waiting for 30 seconds")
    time.sleep(30)

# Call the function to reach and land at the initial latitude and longitude
reach_and_land(initial_lat, initial_lon, landing_altitude)

# 3) Go to each waypoint from waypoint1.json
with open('waypoint1.json', 'r') as file:
    data = json.load(file)
    waypoints = data['waypoints']

print("Going to each waypoint")
vehicle.mode = VehicleMode("GUIDED")

for waypoint in waypoints:
    target_location = LocationGlobalRelative(waypoint['latitude'], waypoint['longitude'], 20)
    vehicle.simple_goto(target_location, groundspeed=10)
    print("Going to waypoint:", target_location)

    while True:
        distance_to_target = get_distance_metres(target_location, vehicle.location.global_relative_frame)
        print(" Distance to target: ", distance_to_target)

        if distance_to_target <= 1.0:
            print("Reached waypoint")
            break
        time.sleep(1)

# 4) Return to Launch (RTL) only after completing the mission
print("Mission completed. Returning to Launch")
vehicle.mode = VehicleMode("RTL")

while True:
    if vehicle.location.global_relative_frame.alt <= 1.0:
        print("Landed at Launch")
        break
    time.sleep(1)

print("Close vehicle object")
vehicle.close()

if sitl:
    sitl.stop()
