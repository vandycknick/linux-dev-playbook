#!/usr/bin/python

import subprocess

from dataclasses import dataclass
from typing import Callable, Optional, Literal, List, Tuple, Dict
from ansible.module_utils.basic import *

@dataclass(frozen=True)
class Extension:
    name: str
    version: str

def list_extensions(executable: Literal["code"], extensions_dir: Optional[str] = None) -> List[Extension]:
    cmd = [executable, "--list-extensions", "--show-versions"]

    if extensions_dir is not None:
        cmd = cmd + ["--extensions-dir", extensions_dir]
    output = subprocess.check_output(cmd, encoding='UTF-8')

    return [
        Extension(name=x[0], version=x[1]) for x in [chunk.split("@") for chunk in output.splitlines()]
    ]


def is_extension_installed(name: str, list_extensions: Callable[[], List[Extension]]) -> bool:
    extensions = list_extensions()
    match = next((ext for ext in extensions if ext.name.lower() == name.lower()), None)
    return match is not None


def install_extension(name: str, executable: Literal["code"], extensions_dir: Optional[str] = None):
    cmd = [executable, "--install-extension", name, "--force"]

    if extensions_dir is not None:
        cmd = cmd + ["--extensions-dir", extensions_dir]


    (status, output) = subprocess.getstatusoutput(" ".join(cmd))

    if status != 0:
        raise Exception(f"TODO: Write some error message {output}")


def install_or_update_extension(name: str, executable: Literal["code"], extensions_dir: Optional[str] = None) -> Tuple[bool, str]:
    list_extensions_in_directory = lambda: list_extensions(executable, extensions_dir)
    extensions = list_extensions_in_directory()
    list_extensions_cache = lambda: extensions

    if is_extension_installed(name, list_extensions_cache):
        extension = next((ext for ext in extensions if ext.name.lower() == name.lower()))
        install_extension(name, executable, extensions_dir)
        updated_extensions = list_extensions_in_directory()
        updated_extension = next((ext for ext in updated_extensions if ext.name.lower() == name.lower()))

        return extension.version != updated_extension.version, "updated"
    else:
        install_extension(name, executable, extensions_dir)
        return True, "installed"


def vscode_extension_present(params: Dict[str, str]):
    name = params["name"]
    extensions_dir = params.get("extensions_dir", None)
    executable = params.get("binary", "code")

    return install_or_update_extension(name, executable, extensions_dir)


def vscode_extension_absent():
    pass


def main():
    fields = {
        "name": { "required": True, "type": "str" },
        "extensions_dir": { "required": False, "type": "str" },
        "binary": {
            "default": "code", 
            "choices": ["code", "code-insiders"],  
            "type": "str"
        },
        "state": {
            "default": "present", 
            "choices": ["present", "absent"],  
            "type": "str"
        },
    }

    choice_map = {
      "present": vscode_extension_present,
      "absent": vscode_extension_absent, 
    }

    module = AnsibleModule(argument_spec=fields, supports_check_mode=False)
    changed, result = choice_map.get(module.params['state'])(module.params)
    
    module.exit_json(changed=changed, meta=result)

if __name__ == "__main__":
    main()
