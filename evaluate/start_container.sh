#!/bin/bash

# Check if the required arguments are provided
if [[ $# -ne 3 ]]; then
    echo "Usage: $0 <repo_name> <memory> <cpuset_cpus>"
    echo "Example: $0 astropy 64g 0-40"
    exit 1
fi

# Arguments
repo_name=$1
memory=$2
cpuset_cpus=$3

# Docker image and container name
image_base="shanchaol/repocod:${repo_name}"
container_name="repocod_${repo_name}"

# Check if a container with the same name is already running or exists
if docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"; then
    echo "Container ${container_name} already exists. Stopping and removing it..."
    docker stop "${container_name}" >/dev/null 2>&1
    docker rm "${container_name}" >/dev/null 2>&1
    echo "Container ${container_name} stopped and removed."
fi

# Start the Docker container
echo "Starting container ${container_name} with memory=${memory}, cpuset_cpus=${cpuset_cpus}..."
docker run -dit --name "${container_name}" --memory "${memory}" --memory-swap "${memory}" --cpuset-cpus="${cpuset_cpus}" "${image_base}" /bin/bash

# Check if the container started successfully
if [[ $? -eq 0 ]]; then
    echo "Container ${container_name} started successfully."
else
    echo "Failed to start container ${container_name}."
fi
