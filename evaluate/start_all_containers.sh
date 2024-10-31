#!/bin/bash

# List of repository names
repo_names=(
  "astropy"
  "requests"
  "plotly.py"
  "flask"
  "sphinx"
  "scikit"
  "seaborn"
  "xarray"
  "datasets"
  "dateutil"
  "more-itertools"
  "sympy"
  "pylint"
)

# Memory and CPU settings
memory="16g"
cpuset_cpus="0-16"

# Loop through each repository name to start a container
for repo in "${repo_names[@]}"; do
    echo "Starting container for ${repo}..."
    ./start_container.sh "$repo" "$memory" "$cpuset_cpus"
done
