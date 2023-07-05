#!/bin/bash

# Open a new terminal window and run land1.py command
gnome-terminal --tab --title="drone1.py" --command="bash -c 'python3 drone1.py --connect tcp:127.0.0.1:5773'"

# Open a new terminal window and run land11.py command
gnome-terminal --tab --title="drone2.py" --command="bash -c 'python3 drone2.py --connect tcp:127.0.0.1:5783'"

# Open a new terminal window and run land111.py command
gnome-terminal --tab --title="drone3.py" --command="bash -c 'python3 drone3.py --connect tcp:127.0.0.1:5793'"