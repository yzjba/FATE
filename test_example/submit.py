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
import abc
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
import uuid


class Cmd(object):
    def __init__(self):
        self._cmd = []

    def add_cmd(self, cmd):
        self._cmd.append(cmd)
        return self

    def rm(self, path):
        self.add_cmd(f"rm {path}")
        return self

    def source(self, path):
        self.add_cmd(f"source {path}")
        return self

    def scp(self, l_path, host, r_path):
        self.add_cmd(f"scp {l_path} {host}:{r_path}")
        return self

    def cd(self, path):
        self.add_cmd(f"cd {path}")
        return self

    def build(self, sep=" && "):
        return sep.join(self._cmd)


class Runner(object):
    def __init__(self):
        self.source = None

    def add_source(self, path):
        self.source = path

    def need_source(self):
        return self.source is not None

    @abc.abstractmethod
    def run_cmd(self, cmd: 'Cmd'):
        pass


class LocalRunner(Runner):
    def __init__(self):
        super().__init__()

    def run_cmd(self, cmd: 'Cmd'):
        uid = uuid.uuid1()
        cmd_str = cmd.build()
        logging.info(f"[CMD({uid})]submit cmd={cmd}")
        subp = subprocess.Popen([cmd_str],
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        stdout, stderr = subp.communicate()
        logging.info(f"[CMD({uid})]stdout={stdout}, stderr={stderr}")
        return stdout.decode("utf-8")


class RemoteRunner(Runner):

    def __init__(self, host):
        super().__init__()
        self._host = host

    def run_cmd(self, cmd: 'Cmd'):
        uid = uuid.uuid1()
        cmd_str = f"ssh {self._host} {cmd.build()}"
        logging.info(f"[CMD({uid})]submit cmd={cmd}")
        subp = subprocess.Popen([cmd_str],
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        stdout, stderr = subp.communicate()
        logging.info(f"[CMD({uid})]stdout={stdout}, stderr={stderr}")
        return stdout.decode("utf-8")

    def scp(self, f_name):
        cmd = Cmd().scp(f_name, self._host, f_name)
        self.run_cmd(cmd)


#
# class AsyncRunner(Runner):
#     raise NotImplementedError()  # todo: async


class Submitter(object):

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

    def upload(self, conf_dict):
        with self._mktemp() as f:
            json.dump(conf_dict, f)
            f.flush()
            return self.submit(f"-f upload -c {f.name}", maybe_scp_files=[f.name])

    def submit_job(self, conf, dsl):
        with self._mktemp() as f_conf:
            with self._mktemp() as f_dsl:
                json.dump(conf, f_conf)
                json.dump(dsl, f_dsl)
                f_conf.flush()
                f_dsl.flush()
                return self.submit(f"-f submit_job -c {f_conf.name} -d {f_dsl.name}")

    def await_finish(self, job_id, timeout=sys.maxsize, check_interval=10):
        deadline = time.time() + timeout
        while True:
            time.sleep(check_interval)
            stdout = self.query_job(job_id)
            status = stdout["data"][0]["f_status"]
            if status == "running" and time.time() < deadline:
                continue
            else:
                return status
