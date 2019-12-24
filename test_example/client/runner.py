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
import abc
import logging
import subprocess
import uuid

from test_example.client.cmd import Cmd


class Runner(object):
    def __init__(self):
        self.source = None

    def add_source(self, path):
        self.source = path

    def need_source(self):
        return self.source is not None

    @abc.abstractmethod
    def run_cmd(self, cmd: 'Cmd'):
        pass


class LocalRunner(Runner):
    def __init__(self):
        super().__init__()

    def run_cmd(self, cmd: 'Cmd'):
        uid = uuid.uuid1()
        cmd_str = cmd.build()
        logging.info(f"[CMD({uid})]submit cmd={cmd}")
        subp = subprocess.Popen([cmd_str],
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        stdout, stderr = subp.communicate()
        logging.info(f"[CMD({uid})]stdout={stdout}, stderr={stderr}")
        return stdout.decode("utf-8")


class RemoteRunner(Runner):

    def __init__(self, host):
        super().__init__()
        self._host = host

    def run_cmd(self, cmd: 'Cmd'):
        uid = uuid.uuid1()
        cmd_str = f"ssh {self._host} {cmd.build()}"
        logging.info(f"[CMD({uid})]submit cmd={cmd}")
        subp = subprocess.Popen([cmd_str],
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        stdout, stderr = subp.communicate()
        logging.info(f"[CMD({uid})]stdout={stdout}, stderr={stderr}")
        return stdout.decode("utf-8")

    def scp(self, f_name):
        cmd = Cmd().scp(f_name, self._host, f_name)
        self.run_cmd(cmd)

#
# class AsyncRunner(Runner):
#     raise NotImplementedError()  # todo: async
