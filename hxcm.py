#!/bin/env python3
# Helix Config Manager - Simple Tool to manage your helix configs
#    Copyright (C) 2024  lz-coder
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

import argparse
import os
import tomllib
import subprocess

tool_name = "hxcm"

user_home = os.path.expanduser("~")
config_path = os.path.join(user_home, f".config/{tool_name}")
config_file_name = f"{tool_name}.toml"
config_file_path = os.path.join(config_path, config_file_name)

config_local_repo = os.path.join(user_home, f".local/share/{tool_name}")
config_remote_repo = None

parser = argparse.ArgumentParser(
    prog="helix-config-manager",
    description="A simple utility to manage helix configs",
    epilog="helix config manager  Copyright (C) 2024  lz-coder",
)

parser.add_argument("-l", "--list", help="List available configs", action="store_true")
parser.add_argument(
    "-s",
    "--sync",
    help="Synchronize local configs database with the configured repository",
    action="store_true",
)
parser.add_argument(
    "-a",
    "--apply",
    nargs=2,
    metavar=("config", "path"),
    help="Apply a config to a given directory",
    action="store",
)


def checkPathAndCreate(path):
    if not os.path.exists(path):
        os.mkdir(path)


if __name__ == "__main__":
    checkPathAndCreate(config_path)

    if not os.path.exists(config_file_path):
        with open(config_file_path, "w") as file:
            file.write("")

    with open(config_file_path, "rb") as file:
        data = tomllib.load(file)

    if "remote_configs_repo" in data.keys():
        config_remote_repo = data["remote_configs_repo"]
    if "local_configs_repo" in data.keys():
        config_local_repo = data["local_configs_repo"]

    checkPathAndCreate(config_local_repo)

    args = parser.parse_args()

    if args.list:
        print("Available configs:")
        available_configs = [
            file for file in os.listdir(config_local_repo) if not file.startswith(".")
        ]
        for i in range(len(available_configs)):
            available_config_path = os.path.join(
                config_local_repo, available_configs[i]
            )
            if os.path.isdir(available_config_path):
                print(available_configs[i])

    elif args.sync:
        if config_remote_repo is not None and not len(config_remote_repo) <= 0:
            print(f"Sinchronizing local config with remote [{config_remote_repo}]")
            local_repo_list = os.listdir(config_local_repo)
            do_sync = False
            if not len(local_repo_list) == 0:
                if ".git" in local_repo_list:
                    subprocess.run(f"git -C {config_local_repo} pull", shell=True)
                else:
                    clear_local_repo = input(
                        "Your local configs repo is not empty. Clear it to syncronize with remote? y or n ? "
                    )
                    if clear_local_repo == "y":
                        subprocess.run(f"rm -rf {config_local_repo}", shell=True)
                        os.mkdir(config_local_repo)
                        do_sync = True
            else:
                do_sync = True

            if do_sync:
                subprocess.run(["git", "clone", config_remote_repo, config_local_repo])
        else:
            print("Remote configs repo not configured")

    elif args.apply:
        config_to_apply = args.apply[0]
        path_config_to_apply = f"{config_local_repo}/{config_to_apply}"
        path_to_apply_config = args.apply[1]

        if os.path.exists(path_config_to_apply):
            helix_config_path = f"{path_to_apply_config}/.helix"
            checkPathAndCreate(helix_config_path)
            subprocess.run(
                f"cp -r {path_config_to_apply}/* {helix_config_path}", shell=True
            )
            print(f"{config_to_apply} configured")
        else:
            print(f"Config {args.apply[0]} not exists in local repo")

    else:
        parser.print_help()
