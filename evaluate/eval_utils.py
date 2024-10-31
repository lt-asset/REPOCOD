import os
import subprocess
import json
import docker
import pdb
import tree_sitter_python as tspython
from tree_sitter import Language, Parser


PY_LANGUAGE = Language(tspython.language())
# Initialize the parser with the Python language
parser = Parser(PY_LANGUAGE)
client = docker.from_env()  # Docker client to interact with Docker

def run_pytest_in_docker(client, container_name, project_path, result_file_name, target_functions_path=None, early_stop=False, n_process = 'auto'):
    """
    Function to run pytest inside a Docker container and check if it completes successfully.

    Args:
        container_name (str): Name of the Docker container.
        project_path (str): Path to the project inside the Docker container.
        result_file_name (str): Path of the file to store the pytest JSON report.

    Returns:
        bool: True if pytest ran successfully, False otherwise.
    """
    try:
        # Get the container
        container = client.containers.get(container_name)
        repo_specific_command = ""
        if "xarray" in project_path:
            repo_specific_command = "/root/miniconda3/bin/conda run -n xarray-tests "
        # Command to run pytest inside the container
        if early_stop:
            if target_functions_path:
                command = f"{repo_specific_command}pytest --continue-on-collection-errors -x --json-report --json-report-file={result_file_name} -n {n_process} --dist=loadfile -v @{target_functions_path}"
            else:
                command = f"{repo_specific_command}pytest --continue-on-collection-errors -x --json-report --json-report-file={result_file_name} -n {n_process} --dist=loadfile -v {project_path}"
        else:
            if target_functions_path:
                command = f"{repo_specific_command}pytest --continue-on-collection-errors --json-report --json-report-file={result_file_name} -n {n_process} --dist=loadfile -v @{target_functions_path}"
            else:
                command = f"{repo_specific_command}pytest --continue-on-collection-errors --json-report --json-report-file={result_file_name} -n {n_process} --dist=loadfile -v {project_path}"
        # print(f"Running command: {command}")

        # Execute the command in the container
        result = container.exec_run(command)

        # Decode output and get the exit code
        output = result.output.decode('utf-8')
        exit_code = result.exit_code
        if exit_code in [1,2,3,4]:
            return False
        elif exit_code == 5:
            return False
        
        return True
    except docker.errors.NotFound:
        print(f"Error: Container '{container_name}' not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False
    
def copy_file_from_docker(container, src_path, dest_path):
    """Copy a file from Docker container to the local system."""
    command = f"docker cp {container.id}:{src_path} {dest_path}"
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # print(f"Successfully copied {src_path} from container to {dest_path}")
    except subprocess.CalledProcessError as e:
        # print(f"Failed to copy file from Docker container: {e}")
        return False
    return True

def copy_file_to_docker(container, src_path, dest_path):
    """Copy a file from the local system to the Docker container."""
    command = f"docker cp {src_path} {container.id}:{dest_path}"
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # print(f"Successfully copied {src_path} to {dest_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to copy file to Docker container: {e}")
            
def execute_command_in_docker(container, command):
    """Execute command inside the Docker container"""
    try:
        exec_result = container.exec_run(command)
        output = exec_result.output.decode('utf-8')
        return exec_result.exit_code
    except Exception as e:
        print(f"Error executing command in Docker: {str(e)}")
        return -1

def check_syntax(file_path):
    try:
        with open(file_path, 'r') as file:
            source_code = file.read()
        compile(source_code, file_path, 'exec')
        # print(f"No syntax errors found in {file_path}.")
    except SyntaxError as e:
        print(f"Syntax error in {file_path} at line {e.lineno}, column {e.offset}: {e.msg}")
    except Exception as e:
        print(f"Error while trying to compile {file_path}: {e}")

def find_subnode_with_name_for_decorated_calls(decorated_call_node, function_name):
    for child_node in decorated_call_node.children:
        if child_node.type == "function_definition":
            child_name_node = child_node.child_by_field_name("name")
            if child_name_node.text.decode() == function_name:
                return child_node
    return None

def find_child_with_name_for_class(current_node, function_name):
    cursor = current_node.walk()
    while(True):
        descentent_node = cursor.node
        if descentent_node.type == "function_definition":
            function_name_node = descentent_node.child_by_field_name("name")
            if function_name_node.text.decode() == function_name:
                return descentent_node
        elif descentent_node.type == "decorated_definition":
            result_node = find_subnode_with_name_for_decorated_calls(descentent_node, function_name)
            if result_node:
                return result_node
        if cursor.goto_first_child():
                continue
        if cursor.goto_next_sibling():
            continue
        while cursor.goto_parent():
            if cursor.goto_next_sibling():
                break
        else:
            break
    return None
        
def remove_function_from_repo(repo_path, function_name, file_path, replace_contents = None):
    """Remove the specified function from the repo."""
    start_line, end_line = None, None
    with open(file_path, 'r') as f:
        code = f.read()
    class_name = None
    if "." in function_name:
        [class_name, function_name] = function_name.split(".")[-2:]
    
    # Parse and modify the file if the function is found
    if not function_name in code:
        if os.path.basename(file_path).replace(".py","") == function_name:
            return False
        raise Exception(f"ERROR: function {function_name} not found in file: {file_path}")
    elif class_name and not class_name in code and class_name != os.path.basename(file_path).replace(".py",""):
        raise Exception(f"ERROR: There should be class name, but class name {class_name} not found in file: {file_path}")

    tree = parser.parse(bytes(code, 'utf8'))
    root_node = tree.root_node
    cursor = root_node.walk()
    new_code_lines = code.splitlines(keepends=True)
    while True:
        node = cursor.node
        if class_name and node.type == "class_definition":
            # if this is the target class
            if class_name == node.child_by_field_name("name").text.decode():
                function_node = find_child_with_name_for_class(node, function_name)
                if function_node:
                    start_line = function_node.start_point[0]
                    end_line = function_node.end_point[0] + 1
                    assert f"def {function_name}" in "".join(new_code_lines[start_line:end_line])
                    break
                else:
                    pdb.set_trace()
        elif (not class_name or class_name == os.path.basename(file_path).replace(".py","")) and node.type == "function_definition":
            function_name_node = node.child_by_field_name("name")
            if function_name_node.text.decode() == function_name:
                start_line = node.start_point[0]
                end_line = node.end_point[0] + 1
                assert f"def {function_name}" in "".join(new_code_lines[start_line:end_line])
                break
        if cursor.goto_first_child():
            continue
        if cursor.goto_next_sibling():
            continue

        while cursor.goto_parent():
            if cursor.goto_next_sibling():
                break
        else:
            break
    if start_line and end_line and start_line < end_line and len(new_code_lines) >= 0:
        with open(file_path, 'w') as f:
            new_code_lines[start_line:end_line] = replace_contents
            f.writelines(new_code_lines)
        return True
    return False
