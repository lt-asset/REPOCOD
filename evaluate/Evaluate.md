# Evaluation
The evaluation process begins by cloning our Docker containers. Then we provide a script to run automatic evaluation. Results will be saved in `./evaluate_results/{infer_result_base_name}`

## Download Docker Images

The Docker images may be updated, so please use the latest version of our Docker images. Use the following command to download Docker images for the 11 repositories used in REPOCOD to your local machine:

`bash download_images.sh`

## Start Containers
Run [`bash ./start_all_containers.sh`](./start_all_containers.sh) to start all your containers. 

We recommend adjusting the memory and CPU settings in the script to fit your system configuration before running it.

## Evaluation

Please use `evaluate.py` to evaluate on REPOCOD.

An example script to start evaluation is: 
```
python evaluate.py path/to/infer_result --clean_up False --early_stop True --n_process 16
```

If you have use the example.py to generate the json file that contains the generation result, you can run 
```
python evaluate.py ../inference/example_seaborn0.json --clean_up False --early_stop True --n_process 16
```
Which will show the evaluation result on the command line and save the result to `./evaluate_results/example_seaborn0.json`
```
Evaluating for instances from Repo: seaborn
    Finished evaluating instance 0, function: Continuous.label, result is False
```

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
