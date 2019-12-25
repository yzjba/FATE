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
from test_example.client.submit import Submitter
from test_example.dsl.io import Linkable, StageOut, StageIn, StageOutData, StageInData, StageOutModel, StageInModel
from test_example.dsl.stage.base import Stage


class Pipe(object):
    def __init__(self):
        self._components = []
        self._indexes = {}
        self._args = None
        self._local_role = "guest"
        self._local_party_id = -1
        self._roles = {}

    def set_local_party(self, role, party_id):
        self._local_role = role
        self._local_party_id = party_id
        return self

    def set_roles(self, **kwargs):
        for role in ["guest", "host", "arbiter"]:
            if role in kwargs:
                if role not in self._roles:
                    self._roles[role] = []
                if isinstance(kwargs[role], list):
                    self._roles[role].extend(kwargs[role])
                else:
                    self._roles[role].append(kwargs[role])
        return self

    def set_name(self, module: 'Stage'):
        self._indexes[module.stage_name] = self._indexes.get(module.stage_name, -1) + 1
        module.name = f"{module.stage_name}_{self._indexes[module.stage_name]}"

    def add_node(self, module: 'Stage'):
        if module in self._components:
            return self
        self._components.append(module)
        return self

    def set_args(self, args):
        self._args = args
        return self

    def link_data(self, src, dst):
        stage_out, out_name = src
        stage_in, in_name = dst

        if not (isinstance(stage_out, StageOutData) and isinstance(stage_in, StageInData)):
            raise ValueError(f"invalid stage_out={stage_out}, stage_in={stage_in}")

        stage_out.link_update(out_name, stage_in, in_name)
        stage_in.link_update(in_name, stage_out, out_name)
        return self

    def link_model(self, src, dst):
        stage_out, out_name = src
        stage_in, in_name = dst

        if not (isinstance(stage_out, StageOutModel) and isinstance(stage_in, StageInModel)):
            raise ValueError(f"invalid stage_out={stage_out}, stage_in={stage_in}")

        stage_out.link_update(out_name, stage_in, in_name)
        stage_in.link_update(in_name, stage_out, out_name)
        return self

    def add_link(self, src, dst):
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

    def run(self, submitter: Submitter):
        job_id = submitter.submit_job(self.conf(), self.dsl())["jobId"]
        submitter.await_job_done(job_id)
        return submitter.query_job(job_id)

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
        return dict(initiator=dict(role=self._local_role, party_id=self._local_party_id),
                    role=self._roles,
                    role_parameters=role_param,
                    algorithm_parameters=global_param)
