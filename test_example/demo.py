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
import os
import time

from test_example.client.runner import LocalRunner
from test_example.client.submit import Submitter
from test_example.dsl import Pipe, DataIO, HomoNN, Args

# create runner and submitter
runner = LocalRunner()
home = os.path.abspath(os.path.join(os.getcwd(), "../"))
submitter = Submitter(runner, home)

# upload data
guest_data = submitter.upload(file="examples/data/breast_homo_guest.csv",
                              namespace="guest", table_name="homo_breast_guest")
host_data = submitter.upload(file="examples/data/breast_homo_host.csv",
                             namespace="host", table_name="homo_breast_host")

# create pipeline
args = Args() \
    .set_train_data([guest_data], role="guest") \
    .set_train_data([host_data], role="host")
data_io = DataIO("DataIO_0")
nn1 = HomoNN("HomoNN_0") \
    .set_batch_size(10)
nn2 = HomoNN("HomoNN_1") \
    .set_batch_size([128, 256], role="host")

pipe = Pipe() \
    .set_local_party("guest", 10000) \
    .set_roles(guest=10000, host=10000, arbiter=10000)
pipe.set_args(args) \
    .add_node(data_io) \
    .add_node(nn1) \
    .add_node(nn2) \
    .link_data(args.out_data.train_data, data_io.in_data.data) \
    .link_data(data_io.out_data.train, nn1.in_data.train_data) \
    .link_data(data_io.out_data.train, nn2.in_data.eval_data) \
    .link_model(nn1.out_model.homo_nn, nn2.in_model.homo_nn)

# submit job
info = pipe.run(submitter)
print(info)
