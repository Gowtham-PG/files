import time
import argparse
from pymavlink import mavutil

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect', help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

# Get the connection string from command-line arguments
connection_string = args.connect

sitl = None

if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()

# Create a MAVLink connection
master = mavutil.mavlink_connection(connection_string)

# Wait for the heartbeat message to ensure a connection is established
master.wait_heartbeat()

# Define the camera trigger command parameters
img_format = 1  # Image format (0: JPEG, 1: RAW)
shutter_speed = 1000  # Shutter speed in milliseconds
iso = 100  # ISO value
exposure_type = 0  # Exposure type (0: Auto, 1: Manual)

# Send the camera trigger command
msg = mavutil.mavlink.MAVLink_message(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL,
    0, 0, 0, 0, 0, 0,
    img_format, 0, 0, shutter_speed, iso, exposure_type)

# Pack the message and send it
master.mav.send(msg)

# Wait for feedback from the drone
while True:
    msg = master.recv_match()
    if msg is not None:
        if msg.get_type() == 'COMMAND_ACK' and msg.command == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL:
            if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                print("Camera trigger command accepted.")
            else:
                print("Camera trigger command failed.")
            break

# Close the connection
master.close()

# Shut down the SITL instance if used
if sitl is not None:
    sitl.stop()
