#!/bin/bash

# Directory to store all repositories
target_dir="../downloaded_repos/"

# List of repository names and their corresponding commit hashes
declare -A repos
repos=(
  ["https://github.com/astropy/astropy.git"]="ee084c73ef45927c374ec6d024a0017ca3422407"
  ["https://github.com/sympy/sympy.git"]="c870d17c2638f5061800e344b72ff80086a0b41d"
  ["https://github.com/PyCQA/pylint.git"]="fa64425da9c59525195e03ef26338cd4be4af2e4"
  ["https://github.com/pallets/flask.git"]="2fec0b206c6e83ea813ab26597e15c96fab08be7"
  ["https://github.com/mwaskom/seaborn.git"]="b4e5f8d261d6d5524a00b7dd35e00a40e4855872"
  ["https://github.com/plotly/plotly.py.git"]="673c19c4eb83709d4344e87976e9fdee697919d3"
  ["https://github.com/scikit-learn/scikit-learn.git"]="c71340fd74280408b84be7ca008e1205e10c7830"
  ["https://github.com/more-itertools/more-itertools.git"]="4dc5e8bc6865b3c8890a0956d0aa4358ab2bc3f9"
  ["https://github.com/sphinx-doc/sphinx.git"]="0a162fa8da21154011a2c890bb82fd0ce96ebf16"
  ["https://github.com/huggingface/datasets.git"]="cdb1d32c5ed026eff8aec5b7068b8f0af07b82cd"
  ["https://github.com/psf/requests.git"]="1ae6fc3137a11e11565ed22436aa1e77277ac98c"
  ["https://github.com/pydata/xarray.git"]="095d47fcb036441532bf6f5aed907a6c4cfdfe0d"
)

# Clone and checkout each repository
for repo_url in "${!repos[@]}"; do
    repo_name=$(basename "$repo_url" .git)
    repo_dir="${target_dir}/${repo_name}"
    commit_hash="${repos[$repo_url]}"

    echo "Processing repository: ${repo_name}"
    
    # Clone the repository if it does not exist
    if [[ ! -d "$repo_dir" ]]; then
        git clone "$repo_url" "$repo_dir"
    fi

    # Enter the repository directory, checkout the specified commit
    if [[ -d "$repo_dir" ]]; then
        cd "$repo_dir" || exit
        git fetch --all
        git checkout "$commit_hash" || echo "Failed to checkout ${commit_hash} in ${repo_name}"
        cd - > /dev/null || exit
    else
        echo "Failed to clone ${repo_name}"
    fi
done

echo "Repositories have been cloned and checked out to specified commits."