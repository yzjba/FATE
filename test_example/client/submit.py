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
import json
import logging
import os
import re
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from string import Template

from test_example.client.cmd import Cmd
from test_example.client.runner import Runner, RemoteRunner


class BaseSubmitter(object):

    def __init__(self, runner, fate_home, work_mode=0, backend=0):
        self._runner: Runner = runner
        self._fate_home = fate_home
        self._flow_client_path = os.path.join(self._fate_home, "fate_flow/fate_flow_client.py")
        self._work_mode = work_mode
        self._backend = backend
        self._tmp_prefix = None

    @property
    def _env_path(self):
        if os.path.isabs(self._runner.source):
            return self._runner.source
        return os.path.join(self._fate_home, self._runner.source)

    def _mktemp(self, mode="w"):
        return tempfile.NamedTemporaryFile(mode=mode, prefix=self._tmp_prefix)

    def set_work_mode(self, mode):
        self._work_mode = mode
        return self

    def set_backend(self, backend):
        self._backend = backend

    def submit(self, cmd, maybe_scp_files=None):
        """
        submit a job to fate_flow
        :param cmd: fate flow cmd
        :param maybe_scp_files: files should scp to remote host when remote runner is used
        :return: stdout of fate_flow submit
        """
        _cmd = Cmd().cd(self._fate_home)
        if self._runner.need_source():
            _cmd.source(self._env_path)
        _cmd.add_cmd(f"python {self._flow_client_path} {cmd}")

        if isinstance(self._runner, RemoteRunner) and maybe_scp_files:
            for f_name in maybe_scp_files:
                self._runner.scp(f_name)
                _cmd.rm(f_name)

        stdout = self._runner.run_cmd(_cmd)
        logging.info(f"[Submit] {stdout}")

        try:
            stdout = json.loads(stdout)
            status = stdout["retcode"]
        except json.decoder.JSONDecodeError:
            raise ValueError(f"[submit_job]fail, stdout:{stdout}")
        if status != 0:
            raise ValueError(f"[submit_job]fail, status:{status}, stdout:{stdout}")
        return stdout

    def query_job(self, job_id):
        return self.submit(cmd=f"-f query_job -j {job_id} -r guest")  # todo: guest?

    def _upload(self, conf_dict):
        with self._mktemp() as f:
            json.dump(conf_dict, f)
            f.flush()
            return self.submit(f"-f upload -c {f.name}", maybe_scp_files=[f.name])

    def upload(self, file, namespace, table_name, head=1, partition=10):
        conf_dict = dict(
            file=file,
            namespace=namespace,
            table_name=table_name,
            head=head,
            partition=partition,
            work_mode=self._work_mode
        )
        self._upload(conf_dict)
        return f"{namespace}.{table_name}"

    def table_info(self, name, namespace):
        return self.submit(f"-f table_info -t {name} -n {namespace}")

    def submit_job(self, conf, dsl):
        with self._mktemp() as f_conf:
            with self._mktemp() as f_dsl:
                print(json.dumps(conf, indent=2))
                conf["job_parameters"] = {"work_mode": self._work_mode}
                json.dump(conf, f_conf)
                json.dump(dsl, f_dsl)
                f_conf.flush()
                f_dsl.flush()
                return self.submit(f"-f submit_job -c {f_conf.name} -d {f_dsl.name}")

    @staticmethod
    def render_template(template_path, **substitute):
        with open(template_path) as f:
            t = Template(f.read())
            return json.loads(t.substitute(**substitute))

    @staticmethod
    def regex_sub(raw_file_path, patten, repl):
        with open(raw_file_path) as f:
            s = f.read()
            return json.loads(re.sub(patten, repl, s))

    @staticmethod
    def await_done(check_func, timeout=sys.maxsize, check_interval=10):
        """
        :raise raise `TimeoutError` if timeout
        """
        deadline = time.time() + timeout
        while True:
            time.sleep(check_interval)
            info, is_done = check_func()
            t = time.time()
            if is_done:
                return info
            if t >= deadline:
                raise TimeoutError()


class Submitter(BaseSubmitter):
    pool = ProcessPoolExecutor()

    def await_job_done(self, job_id, timeout=sys.maxsize, check_interval=10):
        def _check_func():
            info = self.query_job(job_id)["data"][0]["f_status"]
            is_done = info != "running"
            return info, is_done

        return self.await_done(_check_func, timeout, check_interval)


class PoolSubmitter(BaseSubmitter):  # todo: use fixed size queue

    def __init__(self, runner, fate_home, work_mode=0, backend=0, max_workers=1):
        super().__init__(runner, fate_home, work_mode, backend)
        self._pool = ProcessPoolExecutor(max_workers=max_workers)

    def submit(self, cmd, maybe_scp_files=None):
        self._pool.submit(super(PoolSubmitter, self).submit, cmd=cmd, maybe_scp_files=maybe_scp_files)

    def await_job_done(self, job_id, timeout=sys.maxsize, check_interval=10):
        def _check_func():
            info = self.query_job(job_id).result()["data"][0]["f_status"]
            is_done = info != "running"
            return info, is_done

        return self.await_done(_check_func, timeout, check_interval)
