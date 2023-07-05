#!/usr/bin/python2.7

import time
import argparse
import json
import math
from dronekit import connect, VehicleMode, LocationGlobalRelative

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


def arm_and_takeoff(aTargetAltitude):
    print("Basic pre-arm checks")
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialize...")
        time.sleep(1)

    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)

    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


# Define get_distance_metres function
def get_distance_metres(aLocation1, aLocation2):
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


# Define the initial latitude, longitude, and landing altitude
initial_lat = 26.9887067
initial_lon = 80.8985996
landing_altitude = 10

# Set the speed to 15 m/s
speed = 15  # in meters per second

# 1) Go to the initial position
arm_and_takeoff(landing_altitude)

target_location = LocationGlobalRelative(initial_lat, initial_lon, landing_altitude)
print("Going to initial position")
vehicle.simple_goto(target_location, groundspeed=speed)

# Wait until the drone reaches the initial position
while True:
    current_altitude = vehicle.location.global_relative_frame.alt
    distance_to_target = get_distance_metres(target_location, vehicle.location.global_frame)
    print(" Altitude: ", current_altitude)
    print(" Distance to target: ", distance_to_target)

    if distance_to_target <= 1.0:
        print("Reached initial position")
        break
    time.sleep(1)

# Land at a specific latitude and longitude
landing_latitude = 26.9880948   # Latitude of landing location
landing_longitude = 80.9049940  # Longitude of landing location
landing_altitude = 0.2          # Altitude for landing

print("Landing at specific location")

# Set the target location for landing
target_location = LocationGlobalRelative(landing_latitude, landing_longitude, landing_altitude)

# Go to the landing location
vehicle.simple_goto(target_location, groundspeed=speed)

while True:
    current_altitude = vehicle.location.global_relative_frame.alt
    distance_to_target = get_distance_metres(target_location, vehicle.location.global_frame)
    print(" Altitude: ", current_altitude)
    print(" Distance to target: ", distance_to_target)

    if distance_to_target <= 1.0:
        print("Landed at the specified location")
        vehicle.armed = False
        break
    time.sleep(1)

# Close vehicle object
print("Close vehicle object")
vehicle.close()

if sitl:
    sitl.stop()
