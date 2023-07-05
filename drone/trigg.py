import dronekit as dk
import argparse

vehicle = dk.connect("192.168.81.105:14550", wait_ready=True,baud=57600)
vehicle.mode=dk.VehicleMode("GUIDED")
vehicle.armed=True