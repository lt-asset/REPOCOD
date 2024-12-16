# Inference

To perform inference on REPOCOD, we first need to retrieve the necessary repositories. After obtaining these, we can use two provided utility functions to prepare the local repository environment for inference.

## Getting Repositories
For Inference, download the repositiories with the provided hash first. You can do that by running the following script:

```
bash download_repositories.sh
```

This will download the repositories used in REPOCOD to `./downloaded_repos/`

## Getting the repositories snapshots
We provide the util functions `get_problem_instance()` and `reset_instance()` in [inference_utils.py](inference_utils.py).

`get_problem_instance()` can be used to transform the local repository to the repository snapshot needed for a specific instance, and then use the `reset_instance()` to reset it to inference the next instance.

```Python
# Import the dataset and utility functions
from datasets import load_dataset
from inference_utils import get_problem_instance, reset_instance

# Load the REPOCOD dataset, which contains information about various repository functions and test cases
data = load_dataset('lt-asset/REPOCOD')
sample = data['test'][0]  # Retrieve the first sample from the training set

# Details of a dataset sample: https://huggingface.co/datasets/lt-asset/REPOCOD

# Use get_problem_instance to load a snapshot of the repository for the specific sample instance
get_problem_instance(sample)

# Optionally, reset the local repository state to prepare for loading the next instance
# reset_instance(sample)

```

Once the repository snapshot is created, this data instance is ready for generation. For a detailed explanation of the data fields, you can refer to our Huggingface Dataset Card, available [here](https://huggingface.co/datasets/lt-asset/REPOCOD).

A more detailed example code is provided in [example.py](example.py). Once the inference result is generated and save to the correct format as instructed in [../evaluate/Evaluate.md](../evaluate/Evaluate.md), we can use the evaluation scripts to evaluate the generated result.
