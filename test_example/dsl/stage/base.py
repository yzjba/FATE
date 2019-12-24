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

from test_example.dsl.io import HasIn, HasOut
from test_example.dsl.param import HasParam


class Stage(HasIn, HasOut, HasParam):
    def __init__(self, name, stage_name):
        self.stage_name = stage_name
        self.name = name
        HasIn.__init__(self)
        HasOut.__init__(self)
        HasParam.__init__(self, name)

        # override this please!
        self.global_param = {}
        self.role_param = {}

    def dsl(self):
        dsl = {
            "module": self.stage_name,
            "input": {},
            "output": {}
        }
        if self.in_data.dsl():
            dsl["input"]["data"] = self.in_data.dsl()
        if self.in_model.dsl():
            dsl["input"]["model"] = self.in_model.dsl()
        if self.out_data.dsl():
            dsl["output"]["data"] = self.out_data.dsl()
        if self.out_model.dsl():
            dsl["output"]["model"] = self.out_model.dsl()
        return dsl
