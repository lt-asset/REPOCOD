from datasets import load_dataset
from inference_utils import get_problem_instance, reset_instance
import os
import json

data = load_dataset('lt-asset/REPOCOD')
sample = data['train'][0]  # Retrieve the first sample from the training set

# Example structure of a dataset sample:
# From https://huggingface.co/datasets/lt-asset/REPOCOD
# Each sample includes details of a function and relevant metadata from a repository
# "repository": "seaborn",                          # The repository name where the function was collected
# "repo_id": "0",                                   # Unique ID for this sample within the repository
# "target_module_path": "seaborn/_core/scales.py",  # Path to the file where the target function is located
# "prompt": "    def label( 
#     self,
#     formatter: Formatter | None = None, *,        
#     like: str | Callable | None = None,           
#     base: int | None | Default = default,         
#     unit: str | None = None,
# ) -> Continuous: ....",                            # The function signature and any associated docstring
# "relevant_test_path": "/usr/src/app/target_test_cases/failed_tests_Continuous.label.txt", # Path to tests relevant for the function
# "full_function": "    def label(
#     self,
#     formatter: Formatter | None = None, *,
#     like: str | Callable | None = None,
#     base: int | None | Default = default,
#     unit: str | None = None,
# ) -> Continuous: ....",                            # The complete code snippet for the target function
# "function_name": "Continuous.label"               # The full name of the function, including its class

# Use get_problem_instance to load a snapshot of the repository for the specific sample instance
# get_problem_instance() removes the target function body from the local repoistory at `../downloaded_repos/{sample['repository']}`
local_repo_path = get_problem_instance(sample)
modified_path = os.path.join(local_repo_path, sample['target_module_path'])

with open(modified_path, 'r') as f:
    data = f.read()
prefix = data[:data.index(sample['prompt'].strip())]
suffix = data[data.index(sample['prompt'].strip()) + len(sample['prompt'].rstrip()):]

# Reset the local repository state to prepare for loading the next instance
reset_instance(sample)

# Inference example:
# The following code requires installation of transformer and pytorch package
SYSTEM_PROMPT = """You are an exceptionally intelligent coding assistant that consistently delivers accurate and reliable responses to user instructions.
You will be provided a function signiature and the documentation, and your task is to complete the function body.
You must only complete the target function and do not generate any comments or explanation or other functions or an examples. 
You must not leave the target function as `not implemented` or `pass`."""

current_file_template = """This is the file that contains the target function to be generated.

## File path: {}

### Context before the target function
```python
{}
```

### Context after the target function
```python
{}
```

### Target function to complete

```python
{}
"""

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-6.7b-base", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    "deepseek-ai/deepseek-coder-6.7b-base",
    trust_remote_code=True,
    device_map="auto",
    torch_dtype=torch.bfloat16
).cuda()

current_file_prompt = current_file_template.format(sample['target_module_path'], prefix, suffix, sample['prompt'])
input_text = f"{SYSTEM_PROMPT}\n{current_file_prompt}"

inputs = tokenizer(input_text, return_tensors="pt").to("cuda")

output_ids = model.generate(**inputs,
                            max_new_tokens=4096,
                            eos_token_id = tokenizer.encode("```", add_special_tokens=False)[0]
                            )

output = tokenizer.decode(output_ids[0][inputs['input_ids'].size(1):], skip_special_tokens=True)

# Build the result json
gen_dict = {
            sample['repository']: {
                sample['repo_id']: {
                    "function_name": sample['function_name'], 
                    "prompt": current_file_prompt,
                    "output": output
                }
            }
        }

with open("example_seaborn0.json", 'w') as f:
    json.dump(gen_dict, f, indent=2)