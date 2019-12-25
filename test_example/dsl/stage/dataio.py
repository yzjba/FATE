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
from test_example.dsl.stage.base import Stage


class DataIO(Stage):
    def __init__(self, name=None, with_label=True, label_name=None, label_type="int", output_format="dense"):
        super().__init__(name=name, stage_name="DataIO")
        self.global_param = dict(
            with_label=with_label,
            label_type=label_type,
            output_format=output_format
        )
        if label_name is not None:
            self.global_param["label_name"] = label_name = label_name,

    def set_with_label(self, with_label=True, role=None):
        self.__getattr__("set_with_label")(with_label, role)
        return self

    def set_label_type(self, label_type="int", role=None):
        self.__getattr__("set_label_type")(label_type, role)
        return self

    def set_output_format(self, output_format="dense", role=None):
        self.__getattr__("set_output_format")(output_format, role)
        return self

    def set_label_name(self, label_name, role=None):
        self.__getattr__("set_label_name")(label_name, role)
        return self
