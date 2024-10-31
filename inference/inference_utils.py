import os
import subprocess
import docker
import pdb
import tree_sitter_python as tspython
from tree_sitter import Language, Parser


PY_LANGUAGE = Language(tspython.language())
# Initialize the parser with the Python language
parser = Parser(PY_LANGUAGE)
client = docker.from_env()  # Docker client to interact with Docker


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
        
def remove_function_from_repo(function_name, file_path, replace_contents = None):
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

def get_problem_instance(sample, local_repo_path = "../downloaded_repos/"):
    function_name = sample['function_name']
    local_file_path = os.path.join(local_repo_path, sample['repository'], sample["target_module_path"])
    success = remove_function_from_repo(function_name=function_name, file_path=local_file_path, replace_contents=sample['prompt'])
    
    if not success:
        print(f"    Failed to modify repo snapshot at {local_file_path}")
        return False
    else:
        return os.path.join(local_repo_path, sample['repository'])
    
def reset_instance(sample, local_repo_path="../downloaded_repos/"):
    target_module_path = sample["target_module_path"]
    
    local_repo_dir = os.path.join(local_repo_path, sample['repository'])
    original_dir = os.getcwd()
    
    try:
        os.chdir(local_repo_dir)  # Change to repo directory
        
        command = f"git restore {target_module_path}"
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # print(f"Successfully restored {target_module_path} in repository {repo_name}")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Failed to reset file '{target_module_path}' in repository '{sample['repository']}'\nError: {e}")
        return False

    finally:
        os.chdir(original_dir)