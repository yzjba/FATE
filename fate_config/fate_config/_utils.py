#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from pathlib import Path
from ruamel import yaml
import shutil


def get_config_base_path():
    config_dir = Path(__file__).parent.joinpath("conf")
    return config_dir


def get_config_path(name):
    return get_config_base_path().joinpath(name)


def get_fate_env_path():
    return get_config_path("fate.env")


def get_auth_config_path():
    return get_config_path("transfer_conf.yaml")


def load_config(name):
    with get_config_path(name).open() as f:
        return yaml.safe_load(f)


def load_auth_config():
    return load_config("transfer_conf.yaml")


def dump_config(name, config):
    with get_config_path(name).open("r") as f:
        return yaml.safe_dump(config, f)


def copy_config(path, name):
    return shutil.copy(path, get_config_base_path().joinpath(name))


def backup(path, names):
    for name in names:
        shutil.copy(src=get_config_base_path().joinpath(name), dst=path)


def recover(path, names):
    for name in names:
        shutil.copy(src=path, dst=get_config_base_path().joinpath(name))
