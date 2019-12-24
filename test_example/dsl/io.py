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


class Linkable(object):
    def linkable(self, obj):
        raise NotImplemented()


class StageOut(Linkable):
    def __init__(self, parent):
        self.parent = parent
        self._outputs = []

    def link_update(self, name, other, other_name):
        if name not in self._outputs:
            self._outputs.append(name)
        return self

    def __getattr__(self, item):
        return self, item

    def dsl(self):
        return self._outputs


class StageOutModel(StageOut):
    def linkable(self, obj):
        return isinstance(obj, StageInModel)


class StageOutData(StageOut):
    def linkable(self, obj):
        return isinstance(obj, StageInData)


class StageIn(Linkable):

    def __getattr__(self, item):
        return self, item

    def dsl(self):
        return self._inputs

    def link_update(self, name, other, other_name):
        raise NotImplemented()


class StageInData(StageIn):
    def __init__(self, parent):
        self.parent = parent
        self._inputs = {}

    def link_update(self, name, other, other_name):
        if name not in self._inputs:
            self._inputs[name] = []
        self._inputs[name].append(f"{other.parent.name}.{other_name}")
        return self

    def add_input(self, name, value):
        if name not in self._inputs:
            self._inputs[name] = []
        self._inputs[name].append(value)
        return self

    def linkable(self, obj):
        return isinstance(obj, StageOutData)


class StageInModel(StageIn):
    def __init__(self, parent):
        self.parent = parent
        self._inputs = []

    def link_update(self, name, other, other_name):
        if name not in self._inputs:
            self._inputs.append(f"{other.parent.name}.{other_name}")
        return self

    def linkable(self, obj):
        return isinstance(obj, StageOutModel)


class HasIn(object):
    def __init__(self):
        self.in_data = StageInData(self)
        self.in_model = StageInModel(self)


class HasOut(object):
    def __init__(self):
        self.out_data = StageOutData(self)
        self.out_model = StageOutModel(self)
