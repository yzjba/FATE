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

from test_example.dsl.io import Linkable, StageOut, StageIn
from test_example.dsl.stage.base import Stage


class Pipe(object):
    def __init__(self):
        self._components = []
        self._indexes = {}
        self._instances = set()
        self._args = None

    def set_name(self, module: 'Stage'):
        self._indexes[module.stage_name] = self._indexes.get(module.stage_name, -1) + 1
        module.name = f"{module.stage_name}_{self._indexes[module.stage_name]}"

    def add_module(self, module: 'Stage'):
        if module in self._instances:
            return self
        # if module.name is None:
        #     self.set_name(module)
        self._components.append(module)
        self._instances.add(module)
        return self

    def add_args(self, args):
        self._args = args

    def link(self, src, dst):
        stage_out, out_name = src
        stage_in, in_name = dst

        if not (isinstance(stage_out, Linkable) and isinstance(stage_in, Linkable)):
            raise ValueError(f"invalid stage_out={stage_out}, stage_in={stage_in}")
        if not stage_out.linkable(stage_in):
            raise ValueError(f"can't link {stage_out} to {stage_in}")
        if not isinstance(stage_out, StageOut):
            raise ValueError(f"stage_out={stage_out}")
        if not isinstance(stage_in, StageIn):
            raise ValueError(f"stage_in={stage_in}")

        stage_out.link_update(out_name, stage_in, in_name)
        stage_in.link_update(in_name, stage_out, out_name)
        return self

    def run(self, submitter):
        pass

    def dsl(self):
        _dsl = {c.name: c.dsl() for c in self._components}
        return {"components": _dsl}

    def conf(self):
        global_param = {c.name: c.global_param for c in self._components}
        role_param = {}
        for role in ["guest", "host", "arbiter"]:
            role_param[role] = {}
            if self._args is not None:
                if role in self._args.role_param:
                    role_param[role][self._args.name] = self._args.role_param[role]
            for c in self._components:
                if role in c.role_param:
                    role_param[role][c.name] = c.role_param[role]
        return dict(role_parameters=role_param,
                    algorithm_parameters=global_param)
