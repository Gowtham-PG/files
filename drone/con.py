    #!/usr/bin/python2.7

    import time
    import argparse
    import json
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


    arm_and_takeoff(10)

    print("Set default/target airspeed to 3")
    vehicle.airspeed = 3

    point1 = None
    point2 = None

    with open('waypoint1.json', 'r') as file:
        data = json.load(file)
        point1 = LocationGlobalRelative(data['waypoint1']['latitude'], data['waypoint1']['longitude'], 20)
        #point2 = LocationGlobalRelative(data['waypoint2']['latitude'], data['waypoint2']['longitude'], 20)

    vehicle.simple_goto(point1, groundspeed=10)

    time.sleep(40)

    #vehicle.simple_goto(point2, groundspeed=10)

    #time.sleep(30)

    print("Returning to Launch")
    vehicle.mode = VehicleMode("RTL")

    print("Close vehicle object")
    vehicle.close()

    if sitl:
        sitl.stop()

