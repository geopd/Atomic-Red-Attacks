import os
import csv
import fnmatch
import git
import pandas as pd
import yaml

def flat_dictionary(data, prefix='', flat_dict=None):
    if flat_dict is None:
        flat_dict = {}
    
    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            flat_dictionary(value, new_prefix, flat_dict)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_prefix = f"{prefix}.{i}" if prefix else str(i)
            flat_dictionary(item, new_prefix, flat_dict)
    else:
        if prefix in flat_dict:
            flat_dict[prefix] = data
        else:
            flat_dict[prefix] = data
    
    return flat_dict

rows = ['attack_technique', 'display_name', 'name', 'auto_generated_guid', 'description', 'supported_platforms.0', 'supported_platforms.1', 'supported_platforms.2', 'executor.command', 'executor.name', 'executor.elevation_required', 'executor.steps', 'executor.cleanup_command', 'dependency_executor_name', 'dependencies', 'input_arguments']

repo_url = 'https://github.com/redcanaryco/atomic-red-team.git'
git.Repo.clone_from(repo_url, './atomic-red-team', depth=1)

with open('atomic-red-attacks.csv', 'a', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=rows)
    writer.writeheader()
    
    directory = 'atomic-red-team/atomics'
    yaml_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if fnmatch.fnmatch(file, 'T*.yaml'):
                yaml_files.append(os.path.join(root, file))
    
    for file in yaml_files:
        with open(file, "r", encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"Error occurred while loading {file}: {e}")
                continue

        atomic_tests = data['atomic_tests']

        for atomic_test in atomic_tests:
            atomic_flat_dict = flat_dictionary(atomic_test)
            atomic_row_items = {}

            for row in rows:
                if row == 'attack_technique':
                    values = data.get('attack_technique')
                elif row == 'display_name':
                    values = data.get('display_name')
                elif row == 'dependencies':
                    deps = ""
                    for key, value in atomic_flat_dict.items():
                        if key.startswith('dependencies.'):
                            deps += f"{key}: {value}\n"
                    values = deps
                elif row == 'input_arguments':
                    input_args = ""
                    for key, value in atomic_flat_dict.items():
                        if key.startswith('input_arguments.'):
                            input_args += f"{key}: {value}\n\n"
                    values = input_args
                else:
                    values = atomic_flat_dict.get(row, '')
                    
                atomic_row_items[row] = values
            
            writer.writerow(atomic_row_items)
            
csv_read = pd.read_csv('atomic-red-attacks.csv')
markdown_git_table = csv_read.to_markdown(index=False)
with open('atomic-red-attacks.md', 'w', encoding='utf-8') as f:
    f.write(markdown_git_table)