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


class Cmd(object):
    def __init__(self):
        self._cmd = []

    def add_cmd(self, cmd):
        self._cmd.append(cmd)
        return self

    def rm(self, path):
        self.add_cmd(f"rm {path}")
        return self

    def source(self, path):
        self.add_cmd(f"source {path}")
        return self

    def scp(self, l_path, host, r_path):
        self.add_cmd(f"scp {l_path} {host}:{r_path}")
        return self

    def cd(self, path):
        self.add_cmd(f"cd {path}")
        return self

    def build(self, sep=" && "):
        return sep.join(self._cmd)
