# Inference
## Getting Repositories
For Inference, download the repositiories with the provided hash first. You can do that by running the following script:

`bash download_repositories.sh`

This will download the repositories used in REPOCOD to `./downloaded_repos/`

## Getting the repositories snapshots
We provide the util functions `get_problem_instance()` and `reset_instance()` in [inference_utils.py](inference_utils.py).

`get_problem_instance()` can be used to transform the local repository to the repository snapshot needed for a specific instance, and then use the `reset_instance()` to reset it to inference the next instance.

```
from datasets import load_dataset

data = load_dataset('lt-asset/REPOCOD')
    
sample = data['train'][0]

# get the repo snapshot
get_problem_instance(sample)

# reset the local repo to inference the next instance
reset_instance(sample)
```

Once the repository snapshot is created, this data instance is ready for generation. For a detailed explanation of the data fields, you can refer to our Huggingface Dataset Card, available [here](https://huggingface.co/datasets/lt-asset/REPOCOD).