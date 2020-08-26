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
from fate_config._utils import load_config, dump_config
import os


def get_project_base_dir():
    project_base_dir = load_config("service_conf.yaml").get("project_base_dir")
    if not project_base_dir:
        project_base_dir = os.environ.get("PROJECT_BASE_DIR", None)
    if not project_base_dir:
        raise Exception(f"project_base_dir not set")
    return project_base_dir


def load_service_config():
    return load_config("service_conf.yaml")


def dump_service_config(config):
    return dump_config("service_conf.yaml", config)


def get_logs_base_dir():
    return os.path.join(get_project_base_dir(), "logs")


def get_jobs_base_dir():
    return os.path.join(get_project_base_dir(), "jobs")


def get_model_local_cache_base_dir():
    return os.path.join(get_project_base_dir(), "model_local_cache")
