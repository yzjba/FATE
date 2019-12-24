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


class HasParam(object):
    def __init__(self, name):
        self.global_param = {}
        self.role_param = {}

    def set_param(self, name, value, role=None):
        if role is None:
            self._get_global_param()[name] = value
        else:
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
        return name in self.global_param

    def _get_global_param(self):
        return self.global_param

    def _get_or_create_role_param(self, role):
        if role not in self.role_param:
            self.role_param[role] = {}
        return self.role_param[role]
