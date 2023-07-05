#!/usr/bin/python2.7

import time
import argparse
import json
import multiprocessing
from dronekit import connect, VehicleMode, LocationGlobalRelative

def arm_and_takeoff(vehicle, aTargetAltitude):
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

def drone_process(connection_string):
    vehicle = connect(connection_string, wait_ready=True)
    arm_and_takeoff(vehicle, 10)

    print("Set default/target airspeed to 3")
    vehicle.airspeed = 3

    point1 = None
    point2 = None

    with open('waypoints2.json', 'r') as file:
        data = json.load(file)
        point1 = LocationGlobalRelative(data['waypoint1']['latitude'], data['waypoint1']['longitude'], 20)

    vehicle.simple_goto(point1, groundspeed=10)

    time.sleep(30)

    print("Returning to Launch")
    vehicle.mode = VehicleMode("RTL")

    print("Close vehicle object")
    vehicle.close()

    return

if __name__ == '__main__':
    print("Enter the parameters")
    parser = argparse.ArgumentParser(description='Commands vehicles using vehicle.simple_goto.')
    parser.add_argument('--connect', nargs='+', help="Vehicle connection target strings. If not specified, SITL automatically started and used.")
    args = parser.parse_args()

    connection_strings = args.connect
    sitl = None

    if not connection_strings:
        import dronekit_sitl
        sitl = dronekit_sitl.start_default()
        connection_strings = [sitl.connection_string()]

    processes = []
    for connection_string in connection_strings:
        p = multiprocessing.Process(target=drone_process, args=(connection_string,))
        processes.append(p)
        p.start()

    for process in processes:
        process.join()

    if sitl:
        sitl.stop()
