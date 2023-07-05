#!/usr/bin/python2.7

import time
import argparse
import json
from dronekit import connect, VehicleMode, LocationGlobalRelative
from math import sin, cos, sqrt, atan2, radians
from pymavlink import mavutil

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


def calculate_distance(lat1, lon1, lat2, lon2):
    # approximate radius of Earth in meters
    R = 6371000

    # convert coordinates to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # calculate the differences in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # apply Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # calculate the distance
    distance = R * c
    return distance

arm_and_takeoff(10)

print("Set default/target airspeed to 3")
vehicle.airspeed = 10

waypoints = []

with open('optimal_path1.json', 'r') as file:
    data = json.load(file)
    waypoints_data = data['waypoints']
    for waypoint_data in waypoints_data:
        waypoint = LocationGlobalRelative(waypoint_data['latitude'], waypoint_data['longitude'], waypoint_data['altitude'])
        waypoints.append(waypoint)

for waypoint in waypoints:
    vehicle.simple_goto(waypoint, groundspeed=10)
    while vehicle.mode.name == "GUIDED":  # Wait for the drone to reach the waypoint
        remaining_distance = calculate_distance(
            vehicle.location.global_relative_frame.lat,
            vehicle.location.global_relative_frame.lon,
            waypoint.lat,
            waypoint.lon
        )
        print("Distance to waypoint: ", remaining_distance)
        if remaining_distance <= 1:  # Check if the drone has reached the waypoint
            print("Reached waypoint")
            break
        time.sleep(1)

    # Trigger the camera
    mav = vehicle.message_factory.mav.command_long_encode(
        0, 0,  # These values indicate that the message is not intended for a specific target
        mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL,  # Command ID for camera control
        0,  # Confirmation
        1,  # Trigger camera capture
        0, 0, 0, 0, 0, 0  # Other parameters (unused in this case)
    )
    vehicle.send_mavlink(mav)

# Define the additional waypoint coordinates
new_latitude = 26.988514
new_longitude = 80.8933049
new_altitude = 10

# Create a new waypoint
new_waypoint = LocationGlobalRelative(new_latitude, new_longitude, new_altitude)

# Append the new waypoint to the list
waypoints.append(new_waypoint)

# Go to the additional waypoint
vehicle.simple_goto(new_waypoint, groundspeed=10)
while vehicle.mode.name == "GUIDED":
    remaining_distance = calculate_distance(
        vehicle.location.global_relative_frame.lat,
        vehicle.location.global_relative_frame.lon,
        new_waypoint.lat,
        new_waypoint.lon
    )
    print("Distance to additional waypoint: ", remaining_distance)
    if remaining_distance <= 1:
        print("Reached additional waypoint")
        break
    time.sleep(1)

    # Trigger the camera
    mav = vehicle.message_factory.mav.command_long_encode(
        0, 0,  # These values indicate that the message is not intended for a specific target
        mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL,  # Command ID for camera control
        0,  # Confirmation
        1,  # Trigger camera capture
        0, 0, 0, 0, 0, 0  # Other parameters (unused in this case)
    )
    vehicle.send_mavlink(mav)

# Land and disarm the drone
print("Landing...")
vehicle.mode = VehicleMode("LAND")

while True:
    current_altitude = vehicle.location.global_relative_frame.alt
    print(" Altitude: ", current_altitude)

    if current_altitude <= 0.2:
        print("Landed")
        vehicle.armed = False
        break
    time.sleep(1)

while vehicle.armed:  # Wait for the drone to disarm
    print("Waiting for disarming...")
    time.sleep(1)

print("Close vehicle object")
vehicle.close()

if sitl:
    sitl.stop()
