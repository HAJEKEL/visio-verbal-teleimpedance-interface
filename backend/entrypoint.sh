#!/bin/bash

# Exit immediately if any command returns a non-zero status (i.e., fails)
set -e 

# Source the ROS 2 environment setup script to configure the shell
# This sets up environment variables and paths for ROS 2 (Humble) to function correctly
source /opt/ros/humble/setup.bash

# Print the arguments provided to the script
# This can help with debugging by showing what arguments are passed when the script is executed
echo "Provided arguments: $@"

# Execute the command passed as arguments to the script
# This replaces the shell with the command provided, ensuring that the container runs the intended command
exec $@
