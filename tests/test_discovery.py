import os
import sys
import glob

# Add project root to path to allow importing 'commands'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from commands import completion

def test_all_commands_are_in_completion_module_list():
    """Ensures that COMMAND_MODULES in completion.py is up-to-date."""
    commands_dir = os.path.join(project_root, 'commands')
    
    # 1. Find all potential command modules on disk using glob
    found_modules_on_disk = set()
    for f_path in glob.glob(os.path.join(commands_dir, '*.py')):
        module_name = os.path.basename(f_path)[:-3]
        if module_name != '__init__':
            found_modules_on_disk.add(module_name)

    # 2. Get the set of modules registered in completion.py's COMMAND_MODULES
    registered_modules = set()
    for mod in completion.COMMAND_MODULES:
        name = mod.__name__.split('.')[-1]
        registered_modules.add(name)

    # 3. Compare the sets and provide a helpful error message
    missing_from_list = found_modules_on_disk - registered_modules
    extra_in_list = registered_modules - found_modules_on_disk

    assert not missing_from_list, \
        f"The following commands are not registered in `commands/completion.py`'s COMMAND_MODULES list: {missing_from_list}"
    
    assert not extra_in_list, \
        f"The following commands are in `commands/completion.py`'s COMMAND_MODULES list but do not exist as files: {extra_in_list}"