import json
import os
import shutil
import docker
from eval_utils import *
import time
import signal
import argparse

# Define a timeout handler
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException
    
def evaluate_repo(repo_name, result_dict, oracle_dataset = None, eval_result_path = None, tmp_dir = None, clean_up = False, early_stop = True, n_process = 'auto'):
    WORKDIR = "/usr/src/app"
    container_name = f"repocod_{repo_name}"  # Replace with your container name
    docker_origin_project_path = f"{WORKDIR}/{repo_name}_modified/"
    docker_modified_project_path = f"{WORKDIR}/{repo_name}/"
    target_test_cases_dir = 'target_test_cases'
    if os.path.exists(eval_result_path):
        with open(eval_result_path, 'r') as f:
            eval_results = json.load(f)
            if repo_name in eval_results:
                eval_result = eval_results[repo_name]
            else:
                eval_result = {}
    else:
        eval_results = {
            repo_name: {}
        }
        eval_result = {}
    
    recompute = True
    if recompute:
        eval_result = {}
    
    if not tmp_dir:
        tmp_dir = f"tmp_{repo_name}"  # Set this as required
        
    if clean_up:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir,exist_ok=True)
    try:
        container = client.containers.get(container_name)
    except docker.errors.NotFound:
        print(f"Error: Container '{container_name}' not found.")
        return eval_results
    
    infer_results_path = os.path.join(WORKDIR,"infer_results")
    if recompute:
        rm_cmd = f"rm -rf {infer_results_path}"
        exit_code, output = container.exec_run(rm_cmd)
        rm_cmd = f"mkdir -p {infer_results_path}"
        exit_code, output = container.exec_run(rm_cmd)
    
    for k in list(eval_result.keys()):
        if k not in result_dict:
            del eval_result[k]
    print(f"Evaluating for instances from Repo: {repo_name}")
    
    for i, k in enumerate(list(result_dict.keys())):
        if k in eval_result:
            print(f"    Exists result for instance {i}, function: {function_name}, result is {eval_result[k]['result']}")
            continue
        else:
            pass
        function_name = result_dict[k]['function_name']
        sample_start_time = time.time()
        eval_result[k] = {
                'result': False,
                'function_name': function_name,
                'time': 0
            }
        
        target_test_cases = f"{WORKDIR}/{target_test_cases_dir}/failed_tests_{function_name}.txt"
        result_file_name = f"modified_complete_pytest_result_{k}.json"
        infer_result_path = os.path.join(infer_results_path, result_file_name)
        
        oracle_reference = None
        if k in oracle_dataset:
            oracle_reference = oracle_dataset[k]
        else:
            print(f"    Instance {i}, function: {function_name} is not in the dataset")
            continue
        
        target_module_path= oracle_reference["target_module_path"]
        tmp_subfolder = os.path.join(tmp_dir, f"function_{i}")
        os.makedirs(tmp_subfolder, exist_ok=True)
        
        try:
            # continue # comment if want to reset repo
            local_file_path = os.path.join(tmp_subfolder, os.path.basename(target_module_path))
            copy_file_from_docker(container, f"{docker_origin_project_path}{target_module_path}", local_file_path)
            result_dict[k] = result_dict[k]['output']
            if type(result_dict[k]) == list and type(result_dict[k]) != str:
                result_dict[k] = "".join(result_dict[k])
            
            if result_dict[k].strip().startswith("def "):
                replace_contents = result_dict[k].splitlines(True)
            else:
                replace_contents = oracle_reference['prompt'] + result_dict[k].splitlines(True)
                
            success = remove_function_from_repo(repo_path=tmp_dir, function_name=function_name, file_path=local_file_path, replace_contents=replace_contents)
            if not success:
                print(f"    Failed to modify {local_file_path}")
                continue
            check_syntax(local_file_path)
            copy_file_to_docker(container, local_file_path, f"{docker_modified_project_path}{target_module_path}")

            signal.signal(signal.SIGALRM, timeout_handler)
            timeout_duration = 600
            signal.alarm(timeout_duration)

            if repo_name == "scikit-learn":
                test_result = run_pytest_in_docker(client, container_name, os.path.join(docker_modified_project_path, "sklearn"), infer_result_path, target_test_cases, early_stop=True, n_process=n_process)
            else:
                test_result = run_pytest_in_docker(client, container_name, docker_modified_project_path, infer_result_path, target_test_cases, early_stop=True, n_process=n_process)
            
            signal.alarm(0)
            copy_file_from_docker(container, f"{infer_result_path}", os.path.join(tmp_subfolder, "pytest_result.json"))

            if test_result:
                eval_result[k]['result'] = True
                continue

        except TimeoutException:
            container.exec_run(f"cp {docker_origin_project_path}{target_module_path} {docker_modified_project_path}{target_module_path}")
            print("    Execution timed out after 10 minutes.")
            test_result = False
            
        except SystemExit:
            print("    Exiting due to keyboard interrup")
            container.exec_run(f"cp {docker_origin_project_path}{target_module_path} {docker_modified_project_path}{target_module_path}")
            exit()
            
        except Exception as e:
            signal.alarm(0)
            print(f"    Exception occurs for function {k} in {target_module_path}")
            print(e)
            
        finally:
            signal.alarm(0)
            container.exec_run(f"cp {docker_origin_project_path}{target_module_path} {docker_modified_project_path}{target_module_path}")
            eval_result[k]['time'] = time.time() - sample_start_time
            print(f"    Finished evaluating instance {i}, function: {function_name}, result is {eval_result[k]['result']}")
            if i % 10 == 0:
                eval_results[repo_name] = eval_result
                with open(eval_result_path, 'w') as f:
                    json.dump(eval_results, f, indent=2)
                    
    eval_results[repo_name] = eval_result
    return eval_results
        
def evaluate(infer_result_path, clean_up=False, early_stop=True, n_process=8):
    with open(infer_result_path, 'r') as file:
        merged_infer_result = json.load(file)
            
    os.makedirs("./evaluate_results", exist_ok=True)
    eval_result_path = f"./evaluate_results/{os.path.basename(infer_result_path)}"
    result_signature = "pytest_results/" + os.path.basename(infer_result_path)[:-len(".json")]

    oracle_dataset_path = f"../ref_dataset.json"
    if os.path.exists(oracle_dataset_path):
        with open(oracle_dataset_path, 'r') as f:
            oracle_datasets = json.load(f)
    else:
        print("Incorrect oracle dataset path, exiting")
        exit()
        
    for repo_name in merged_infer_result:
        if repo_name in oracle_datasets:
            oracle_dataset = oracle_datasets[repo_name]
        tmp_dir = f"{result_signature}/{repo_name}/"
        eval_results = evaluate_repo(repo_name, merged_infer_result[repo_name], oracle_dataset, eval_result_path, tmp_dir, clean_up=clean_up, early_stop=early_stop, n_process=n_process)
        with open(eval_result_path, 'w') as f:
            json.dump(eval_results, f, indent=2)
    
    return eval_results
 
def main():
    parser = argparse.ArgumentParser(description="Run evaluation with specified parameters.")
    parser.add_argument("infer_result_path", type=str, help="Path to the inference result file")
    parser.add_argument("--clean_up", type=bool, default=False, help="Whether to clean up after evaluation (default: False)")
    parser.add_argument("--early_stop", type=bool, default=True, help="Whether to stop once a pytest error is met (default: True)")
    parser.add_argument("--n_process", type=int, default=8, help="Number of processes to use (default: 8)")

    # Parse arguments
    args = parser.parse_args()

    # Call evaluate with parsed arguments
    evaluate(args.infer_result_path, args.clean_up, args.early_stop, args.n_process)

    
if __name__ == "__main__":
    main()