# Evaluation
The evaluation process begins by cloning our Docker containers. Then we provide a script to run automatic evaluation. Results will be saved in `./evaluate_results/{infer_result_base_name}`

## Download Docker Images

Use the following command to download Docker images for the 11 repositories used in REPOCOD to your local machine:

`bash download_images.sh`

## Start Containers
Run [`bash ./start_all_containers.sh`](./start_all_containers.sh) to start all your containers. 

We recommend adjusting the memory and CPU settings in the script to fit your system configuration before running it.

## Evaluation

Please use `evaluate.py` to evaluate on REPOCOD.

An example script to start evaluation is: `python evaluate.py path/to/infer_result --clean_up False --early_stop True --n_process 16`.

We recommend setting n_process to match the number of CPUs allocated in the previous step.

### Important: Required Input Format for Evaluation

The input file should follow this format, with function_name matching the names provided in the dataset.

```{
    ...
    "seaborn": {
      ...
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