#!/usr/bin/python2.7

import time
import argparse
import json
import math
from dronekit import connect, VehicleMode, LocationGlobalRelative

parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect1', help="Vehicle 1 connection target string.")
parser.add_argument('--connect2', help="Vehicle 2 connection target string.")
parser.add_argument('--connect3', help="Vehicle 3 connection target string.")
args = parser.parse_args()

connection_strings = [args.connect1, args.connect2, args.connect3]
vehicles = []

for connection_string in connection_strings:
    vehicle = connect(connection_string, wait_ready=True)
    vehicles.append(vehicle)

# Define get_distance_metres function
def get_distance_metres(aLocation1, aLocation2):
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat * dlat) + (dlong * dlong)) * 1.113195e5

def reach_and_land(vehicle, target_lat, target_lon, target_altitude):
    print("Going to initial position")
    target_location = LocationGlobalRelative(target_lat, target_lon, target_altitude)

    while True:
        distance_to_target = get_distance_metres(target_location, vehicle.location.global_relative_frame)
        print(" Distance to target: ", distance_to_target)

        if distance_to_target < 1:
            print("Reached target location")
            break
        time.sleep(1)

    print("Landing")
    vehicle.mode = VehicleMode("LAND")

def arm_and_takeoff(vehicle, target_lat, target_lon, target_altitude):
    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print("Waiting for arming...")
        time.sleep(1)

    print("Taking off")
    vehicle.simple_takeoff(target_altitude)

    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

def go_to_waypoints(vehicle, waypoint_file):
    print("Going to waypoints")
    with open(waypoint_file) as file:
        data = json.load(file)

    waypoints = data['waypoints']

    for waypoint in waypoints:
        target_lat = float(waypoint['latitude'])
        target_lon = float(waypoint['longitude'])
        target_altitude = float(waypoint['altitude'])

        target_location = LocationGlobalRelative(target_lat, target_lon, target_altitude)

        while True:
            distance_to_target = get_distance_metres(target_location, vehicle.location.global_frame)
            print(" Distance to target: ", distance_to_target)

            if distance_to_target < 1:
                print("Reached waypoint")
                break
            vehicle.simple_goto(target_location)
            time.sleep(1)

        time.sleep(1)


# Define initial positions for each drone
initial_positions = [
    (26.9887067, 80.8985996),
    (26.9886684, 80.8903170),
    (26.9890508, 80.8832359)
]

# Define waypoints JSON files for each drone
waypoint_files = [
    'waypoint1.json',
    'waypoint2.json',
    'waypoint3.json'
]

# Arm and takeoff for each drone
for i, vehicle in enumerate(vehicles):
    initial_lat, initial_lon = initial_positions[i]
    arm_and_takeoff(vehicle, initial_lat, initial_lon, 10)

# Wait for 30 seconds after reaching the initial position
time.sleep(30)

# Go to waypoints for each drone
for i, vehicle in enumerate(vehicles):
    waypoint_file = waypoint_files[i]
    go_to_waypoints(vehicle, waypoint_file)

# RTL for each drone
for vehicle in vehicles:
    print("Returning to Launch")
    vehicle.mode = VehicleMode("RTL")

# Close vehicle objects
for vehicle in vehicles:
    print("Closing vehicle object")
    vehicle.close()
