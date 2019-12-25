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
from test_example.dsl.io import HasOut
from test_example.dsl.param import HasParam


class Args(HasOut, HasParam):
    def __init__(self):
        self.name = "args"
        HasOut.__init__(self)
        HasParam.__init__(self, self.name)
        self.global_param = {"data": {}}

    def set_param(self, name, value, role=None):
        if role is None:
            raise ValueError("")
        else:
            for i in range(len(value)):
                n = value[i]
                if isinstance(n, str):
                    _namespace, _name = n.split(".")
                    value[i] = dict(namespace=_namespace, name=_name)
            self._get_or_create_role_param(role)[name] = value
        return self

    def setter_factory(self, name):
        def _fn(value, role=None):
            return self.set_param(name, value, role)

        return _fn

    def __getattr__(self, item):
        prefix = "set_"
        if isinstance(item, str) and item.startswith(prefix):
            name = item[len(prefix):]
            if self._is_param(name):
                return self.setter_factory(name)

    def _is_param(self, name):
        return True

    def _get_global_param(self):
        return self.global_param["data"]

    def _get_or_create_role_param(self, role):
        if role not in self.role_param:
            _role = {}
            self.role_param[role] = {"data": _role}
        return self.role_param[role]["data"]
