# Evaluation
The evaluation process first requires to clone our docker containers.

## Download Docker Images
`bash download_images.sh`

## Start Containers
We recommand fit the Memory and CPU settings to your system in [here](./start_all_containers.sh) before running the following script
`bash start_all_containers.sh`

## Evaluation
There are several optional arguments to set for evaluation.
An example script to start evaluation is: `python evaluate.py path/to/infer_result --clean_up False --early_stop True --n_process 16`.

The infer_result should have the following format, the function_name needs to be the same as the dataset.json:
```{
    ...
    "seaborn": {
      "28": {
        "function_name": "axisgrid.PairGrid.__init__", 
        "prompt": "You are an ....",
        "output": "        self.data = data\n        self.hue = hue\n...."
      },
      {
        more functions here
        ...
      }
      ...
    },
    ...
}
```