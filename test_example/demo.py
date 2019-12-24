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

from test_example.client.runner import LocalRunner
from test_example.client.submit import Submitter
from test_example.dsl import Pipe, DataIO, HomoNN, Args


def main():
    pipe = Pipe()
    args = Args().set_train_data([
        {
            "name": "homo_breast_guest",
            "namespace": "homo_breast_guest"
        }
    ], role="guest").set_train_data([
        {
            "name": "homo_breast_host",
            "namespace": "homo_breast_host"
        }
    ], role="host")
    pipe.add_args(args)
    data_io = DataIO("DataIO_0")
    nn1 = HomoNN("HomoNN_0").set_batch_size(10)
    nn2 = HomoNN("HomoNN_1").set_batch_size([128, 256], role="host")
    pipe.add_module(data_io) \
        .add_module(nn1) \
        .add_module(nn2) \
        .link(args.out_data.train_data, data_io.in_data.data) \
        .link(data_io.out_data.train, nn1.in_data.train_data) \
        .link(data_io.out_data.train, nn2.in_data.eval_data) \
        .link(nn1.out_model.homo_nn, nn2.in_model.homo_nn)

    runner = LocalRunner()
    home = os.path.abspath(os.path.join(os.getcwd(), "../"))
    submitter = Submitter(runner, home)
    conf = pipe.conf()
    conf["initiator"] = {
        "role": "guest",
        "party_id": 10000
    }
    conf["role"] = {
        "guest": [
            10000
        ],
        "host": [
            10000
        ],
        "arbiter": [
            10000
        ]
    }
    job_id = submitter.submit_job(conf, pipe.dsl())["jobId"]
    submitter.await_job_done(job_id)
    print(submitter.query_job(job_id))


if __name__ == '__main__':
    main()
