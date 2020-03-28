#!/bin/bash

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

set -e
cwd=$(
  cd $(dirname $0)
  pwd
)
cd ${cwd}
source_code_dir=$(
  cd $(dirname ${cwd})
  cd ../
  pwd
)
echo "[INFO] Source code dir is ${source_code_dir}"
packages_dir=${source_code_dir}/cluster-deploy/packages
#mkdir -p ${packages_dir}

eggroll_download() {
  cd ${source_code_dir}
  eggroll_git_url=$(grep -A 3 "eggroll_$1" .gitmodules | grep 'url' | awk -F '= ' '{print $2}')
  eggroll_git_branch=$(grep -A 3 "eggroll_$1" .gitmodules | grep 'branch' | awk -F '= ' '{print $2}')
  echo "[INFO] Git clone eggroll submodule source code from ${eggroll_git_url} branch ${eggroll_git_branch}"
  if [[ -e "eggroll_$1" ]]; then
    while [[ true ]]; do
      read -p "The eggroll_$1 directory already exists, delete and re-download? [y/n] " input
      case ${input} in
      [yY]*)
        echo "[INFO] Delete the original eggroll_$1"
        rm -rf eggroll_$1
        git clone ${eggroll_git_url} -b ${eggroll_git_branch} eggroll_$1
        break
        ;;
      [nN]*)
        echo "[INFO] Use the original eggroll_$1"
        break
        ;;
      *)
        echo "Just enter y or n, please."
        ;;
      esac
    done
  else
    git clone ${eggroll_git_url} -b ${eggroll_git_branch} eggroll_$1
  fi
}

fateboard_download() {
  cd ${source_code_dir}
  fateboard_git_url=$(grep -A 3 '"fateboard"' .gitmodules | grep 'url' | awk -F '= ' '{print $2}')
  fateboard_git_branch=$(grep -A 3 '"fateboard"' .gitmodules | grep 'branch' | awk -F '= ' '{print $2}')
  echo "[INFO] Git clone fateboard submodule source code from ${fateboard_git_url} branch ${fateboard_git_branch}"
  if [[ -e "fateboard" ]]; then
    while [[ true ]]; do
      read -p "The fateboard directory already exists, delete and re-download? [y/n] " input
      case ${input} in
      [yY]*)
        echo "[INFO] Delete the original fateboard"
        rm -rf fateboard
        git clone ${fateboard_git_url} -b ${fateboard_git_branch} fateboard
        break
        ;;
      [nN]*)
        echo "[INFO] Use the original fateboard"
        break
        ;;
      *)
        echo "Just enter y or n, please."
        ;;
      esac
    done
  else
    git clone ${fateboard_git_url} -b ${fateboard_git_branch} fateboard
  fi

}

config_init() {
  if [[ $1 == "1x" ]]; then
    egg_version=$(grep -E -m 1 -o "<eggroll.version>(.*)</eggroll.version>" ${source_code_dir}/eggroll_1x/pom.xml | tr -d '[\\-a-z<>//]' | awk -F "eggroll.version" '{print $2}')
    meta_service_version=$(grep -E -m 1 -o "<eggroll.version>(.*)</eggroll.version>" ${source_code_dir}/eggroll_1x/pom.xml | tr -d '[\\-a-z<>//]' | awk -F "eggroll.version" '{print $2}')
    roll_version=$(grep -E -m 1 -o "<eggroll.version>(.*)</eggroll.version>" ${source_code_dir}/eggroll_1x/pom.xml | tr -d '[\\-a-z<>//]' | awk -F "eggroll.version" '{print $2}')
    federation_version=$(grep -E -m 1 -o "<fate.version>(.*)</fate.version>" ${source_code_dir}/arch/pom.xml | tr -d '[\\-a-z<>//]' | awk -F "fte.version" '{print $2}')
    proxy_version=$(grep -E -m 1 -o "<fate.version>(.*)</fate.version>" ${source_code_dir}/arch/pom.xml | tr -d '[\\-a-z<>//]' | awk -F "fte.version" '{print $2}')

    sed -i.bak "s/egg_version=.*/egg_version=${egg_version}/g" ${source_code_dir}/cluster-deploy/scripts/default_configurations.sh
    sed -i.bak "s/meta_service_version=.*/meta_service_version=${meta_service_version}/g" ${source_code_dir}/cluster-deploy/scripts/default_configurations.sh
    sed -i.bak "s/roll_version=.*/roll_version=${roll_version}/g" ${source_code_dir}/cluster-deploy/scripts/default_configurations.sh
    sed -i.bak "s/federation_version=.*/federation_version=${federation_version}/g" ${source_code_dir}/cluster-deploy/scripts/default_configurations.sh
    sed -i.bak "s/proxy_version=.*/proxy_version=${proxy_version}/g" ${source_code_dir}/cluster-deploy/scripts/default_configurations.sh
  fi
  fateboard_version=$(grep -E -m 1 -o "<version>(.*)</version>" ${source_code_dir}/fateboard/pom.xml | tr -d '[\\-a-z<>//]' | awk -F "version" '{print $2}')
  sed -i.bak "s/fateboard_version=.*/fateboard_version=${fateboard_version}/g" ${source_code_dir}/cluster-deploy/scripts/default_configurations.sh
  source ${source_code_dir}/cluster-deploy/scripts/default_configurations.sh
}

eggroll_1x_compile() {
  eggroll_source_code_dir=${source_code_dir}/eggroll_1x
  cd ${eggroll_source_code_dir}
  echo "[INFO] Compiling eggroll_1x start"
  mvn clean package -DskipTests
  echo "[INFO] Compile eggroll_1x done"

  echo "[INFO] Moving eggroll_1x start"

  cd ${eggroll_source_code_dir}
  cd api
  tar czf eggroll-api-${version}.tar.gz *
  mv eggroll-api-${version}.tar.gz ${packages_dir}/

  cd ${eggroll_source_code_dir}
  cd computing
  tar czf eggroll-computing-${version}.tar.gz *
  mv eggroll-computing-${version}.tar.gz ${packages_dir}/

  cd ${eggroll_source_code_dir}
  cd conf
  tar czf eggroll-conf-${version}.tar.gz *
  mv eggroll-conf-${version}.tar.gz ${packages_dir}/

  cd ${eggroll_source_code_dir}
  cd framework/egg/target
  tar czf eggroll-egg-${version}.tar.gz eggroll-egg-${egg_version}.jar lib/
  mv eggroll-egg-${version}.tar.gz ${packages_dir}/

  cd ${eggroll_source_code_dir}
  cd framework/meta-service/target
  tar czf eggroll-meta-service-${version}.tar.gz eggroll-meta-service-${meta_service_version}.jar lib/
  mv eggroll-meta-service-${version}.tar.gz ${packages_dir}/

  cd ${eggroll_source_code_dir}
  cd framework/roll/target
  tar czf eggroll-roll-${version}.tar.gz eggroll-roll-${roll_version}.jar lib/
  mv eggroll-roll-${version}.tar.gz ${packages_dir}/

  cd ${eggroll_source_code_dir}
  cd storage/storage-service-cxx
  tar czf eggroll-storage-service-cxx-${version}.tar.gz *
  mv eggroll-storage-service-cxx-${version}.tar.gz ${packages_dir}/
  echo "[INFO] Moving eggroll_1x done"

}

fate_compile() {
  echo "[INFO] Compiling fate start"
  cd ${source_code_dir}/fateboard/
  mvn clean package -DskipTests
  if [ $1 == "1x" ]; then
    cd ${source_code_dir}
    mv eggroll_1x eggroll
    cd ${source_code_dir}/arch/
    mvn clean package -DskipTests
    cd ${source_code_dir}
    mv eggroll eggroll_1x
  fi
  echo "[INFO] Compile fate done"
}
eggroll_1x_package() {
  rm -rf ${packages_dir}/eggroll_1x
  echo "[INFO] Package egg start"
  mkdir -p ${packages_dir}/eggroll_1x/egg
  cd ${packages_dir}/eggroll_1x/egg
  mv ${packages_dir}/eggroll-egg-${version}.tar.gz ./
  tar xzf eggroll-egg-${version}.tar.gz
  rm -rf eggroll-egg-${version}.tar.gz
  ln -s eggroll-egg-${egg_version}.jar eggroll-egg.jar

  #	cp ${cwd}/deploy/eggroll/egg/modify_json.py ./
  cp ${source_code_dir}/eggroll_1x/framework/egg/src/main/resources/processor-starter.sh ./
  mkdir conf
  cp ${source_code_dir}/eggroll_1x/framework/egg/src/main/resources/egg.properties ./conf
  cp ${source_code_dir}/eggroll_1x/framework/egg/src/main/resources/log4j2.properties ./conf
  cp ${source_code_dir}/eggroll_1x/framework/egg/src/main/resources/applicationContext-egg.xml ./conf
  echo "[INFO] Package egg done"

  echo "[INFO] Package storage-service-cxx start"
  mkdir -p ${packages_dir}/eggroll_1x/storage-service-cxx
  cd ${packages_dir}/eggroll_1x/storage-service-cxx
  mv ${packages_dir}/eggroll-storage-service-cxx-${version}.tar.gz ./
  tar xzf eggroll-storage-service-cxx-${version}.tar.gz
  rm -rf eggroll-storage-service-cxx-${version}.tar.gz
  get_module_package ${source_code_dir} "storage-service-cxx third-party" third_party_eggrollv1.tar.gz
  get_module_package ${source_code_dir} "storage-service-cxx third-party" third_party_eggrollv1_ubuntu.tar.gz
  tar xzf third_party_eggrollv1.tar.gz
  rm -rf third_party_eggrollv1.tar.gz
  rm -rf ${packages_dir}/third_party_eggrollv1.tar.gz
  tar xzf third_party_eggrollv1_ubuntu.tar.gz
  rm -rf third_party_eggrollv1_ubuntu.tar.gz
  rm -rf ${packages_dir}/third_party_eggrollv1_ubuntu.tar.gz
  echo "[INFO] Package storage-service-cxx done"

  echo "[INFO] Package eggroll start"
  mkdir -p ${packages_dir}/eggroll_1x/python/eggroll/computing
  cd ${packages_dir}/eggroll_1x/python/eggroll/computing
  mv ${packages_dir}/eggroll-computing-${version}.tar.gz ./
  tar xzf eggroll-computing-${version}.tar.gz
  rm -rf eggroll-computing-${version}.tar.gz

  mkdir -p ${packages_dir}/eggroll_1x/python/eggroll/api
  cd ${packages_dir}/eggroll_1x/python/eggroll/api
  mv ${packages_dir}/eggroll-api-${version}.tar.gz ./
  tar xzf eggroll-api-${version}.tar.gz
  rm -rf eggroll-api-${version}.tar.gz

  mkdir ${packages_dir}/eggroll_1x/python/eggroll/conf
  cd ${packages_dir}/eggroll_1x/python/eggroll/conf
  mv ${packages_dir}/eggroll-conf-${version}.tar.gz ./
  tar xzf eggroll-conf-${version}.tar.gz
  rm -rf eggroll-conf-${version}.tar.gz
  #	cp ${cwd}/deploy/eggroll/egg/modify_json.py ./

  echo "[INFO] Package eggroll done"

  cp ${source_code_dir}/cluster-deploy/scripts/deploy/eggroll/services.sh ./

  echo "[INFO] Package meta-service start"
  mkdir -p ${packages_dir}/eggroll_1x/meta-service
  cd ${packages_dir}/eggroll_1x/meta-service
  mv ${packages_dir}/eggroll-meta-service-${version}.tar.gz ./
  tar xzf eggroll-meta-service-${version}.tar.gz
  rm -rf eggroll-meta-service-${version}.tar.gz
  ln -s eggroll-meta-service-${meta_service_version}.jar eggroll-meta-service.jar

  mkdir conf
  cp ${source_code_dir}/eggroll_1x/framework/meta-service/src/main/resources/meta-service.properties ./conf
  cp ${source_code_dir}/eggroll_1x/framework/meta-service/src/main/resources/log4j2.properties ./conf
  cp ${source_code_dir}/eggroll_1x/framework/meta-service/src/main/resources/applicationContext-meta-service.xml ./conf
  echo "[INFO] Package meta-service done"

  echo "[INFO] Package roll start"
  mkdir -p ${packages_dir}/eggroll_1x/roll
  cd ${packages_dir}/eggroll_1x/roll
  mv ${packages_dir}/eggroll-roll-${version}.tar.gz ./
  tar xzf eggroll-roll-${version}.tar.gz
  rm -rf eggroll-roll-${version}.tar.gz
  ln -s eggroll-roll-${roll_version}.jar eggroll-roll.jar

  mkdir conf
  cp ${source_code_dir}/eggroll_1x/framework/roll/src/main/resources/roll.properties ./conf
  cp ${source_code_dir}/eggroll_1x/framework/roll/src/main/resources/log4j2.properties ./conf
  cp ${source_code_dir}/eggroll_1x/framework/roll/src/main/resources/applicationContext-roll.xml ./conf
  echo "[INFO] Package roll done"
}

eggroll_2x_package() {
  rm -rf ${packages_dir}/eggroll_2x
  cd ${source_code_dir}/eggroll_2x
  echo "[INFO] Package eggroll start"
  sh deploy/auto-packaging.sh
  mkdir -p ${packages_dir}/eggroll_2x
  mv eggroll.tar.gz ${packages_dir}/eggroll_2x
  cd ${packages_dir}/eggroll_2x
  tar -xzf eggroll.tar.gz
  rm eggroll.tar.gz
  echo "[INFO] Package eggroll done"
}

fateboard_package() {
  rm -rf ${packages_dir}/fateboard
  echo "[INFO] Packaging fateboard start"
  mkdir -p ${packages_dir}/fateboard
  cd ${packages_dir}/fateboard
  cp ${source_code_dir}/fateboard/target/fateboard-${fateboard_version}.jar ./
  mkdir conf ssh
  touch ./ssh/ssh.properties
  cp ${source_code_dir}/fateboard/src/main/resources/application.properties ./conf
  ln -s fateboard-${fateboard_version}.jar fateboard.jar
  cp ${cwd}/deploy/fateboard/service.sh ./
  echo "[INFO] Packaging fateboard done"
}

federation_package() {
  rm -rf ${packages_dir}/federation
  echo "[INFO] Packaging federation start"
  mkdir -p ${packages_dir}/federation
  cd ${source_code_dir}/arch/driver/federation/target
  cp -r fate-federation-${federation_version}.jar lib/ ${packages_dir}/federation/
  cd ${packages_dir}/federation
  mkdir conf
  cp ${source_code_dir}/arch/driver/federation/src/main/resources/federation.properties ./conf
  cp ${source_code_dir}/arch/driver/federation/src/main/resources/log4j2.properties ./conf
  cp ${source_code_dir}/arch/driver/federation/src/main/resources/applicationContext-federation.xml ./conf
  ln -s fate-federation-${federation_version}.jar fate-federation.jar
  cp ${cwd}/deploy/federation/service.sh ./
  #  cp ${cwd}/federation/configurations.sh ../
  echo "[INFO] Packaging federation done"
}

proxy_package() {
  rm -rf ${packages_dir}/proxy
  echo "[INFO] Packaging proxy start"
  mkdir -p ${packages_dir}/proxy
  cd ${source_code_dir}/arch/networking/proxy/target
  cp -r fate-proxy-${proxy_version}.jar lib/ ${packages_dir}/federation/
  cd ${packages_dir}/proxy
  mkdir conf
  cp ${source_code_dir}/arch/networking/proxy/src/main/resources/proxy.properties ./conf
  cp ${source_code_dir}/arch/networking/proxy/src/main/resources/log4j2.properties ./conf
  cp ${source_code_dir}/arch/networking/proxy/src/main/resources/applicationContext-proxy.xml ./conf
  cp ${source_code_dir}/arch/networking/proxy/src/main/resources/route_tables/route_table.json ./conf
  ln -s fate-proxy-${proxy_version}.jar fate-proxy.jar
  cp ${cwd}/deploy/proxy/service.sh ./
  #  cp ${cwd}/proxy/configurations.sh ${cwd}/proxy/proxy_modify_json.py ../
  echo "[INFO] Packaging proxy done"
}

federatedml_package() {
  rm -rf ${packages_dir}/federatedml
  echo "[INFO] Packaging federatedml start"
  cp -r ${source_code_dir}/federatedml ${packages_dir}/
  echo "[INFO] Packaging federatedml done"
}

examples_package() {
  rm -rf ${packages_dir}/examples
  echo "[INFO] Packaging examples start"
  cp -r ${source_code_dir}/examples ${packages_dir}/
  echo "[INFO] Packaging examples done"
}

federatedrec_package() {
  rm -rf ${packages_dir}/federatedrec
  echo "[INFO] Packaging federatedrec start"
  cp -r ${source_code_dir}/federatedrec ${packages_dir}/
  echo "[INFO] Packaging federatedrec done"
}

arch_package() {
  rm -rf ${packages_dir}/arch
  echo "[INFO] Packaging arch start"
  mkdir -p ${packages_dir}/arch
  cd ${packages_dir}/arch
  cp -r ${source_code_dir}/arch/api ./
  mkdir conf
  cp ${source_code_dir}/arch/conf/server_conf.json ./conf
  echo "[INFO] Packaging arch done"
}

fate_flow_package() {
  rm -rf ${packages_dir}/fate_flow
  echo "[INFO] Packaging fate_flow start"
  #  mkdir -p ${packages_dir}/fate_flow
  cp -r ${source_code_dir}/fate_flow ${packages_dir}/
  echo "[INFO] Packaging fate_flow done"
}

jdk_package() {
  rm -rf ${packages_dir}/jdk
  echo "[INFO] Packaging jdk start"
  mkdir -p ${packages_dir}/jdk
  cd ${packages_dir}/jdk
  get_module_package ${source_code_dir} "jdk" jdk-${jdk_version}-linux-x64.tar.gz
  mv ${packages_dir}/jdk-${jdk_version}-linux-x64.tar.gz ./
  tar xzf jdk-${jdk_version}-linux-x64.tar.gz
  rm -rf jdk-${jdk_version}-linux-x64.tar.gz
  mkdir tmp
  cp -r jdk*/* tmp
  rm -rf jdk*
  mv tmp jdk-${jdk_version}
  echo "[INFO] Packaging jdk done"
}

mysql_package() {
  rm -rf ${packages_dir}/mysql
  echo "[INFO] Packaging mysql start"
  mkdir -p ${packages_dir}/mysql
  cd ${packages_dir}/mysql
  get_module_package ${source_code_dir} "mysql" mysql-${mysql_version}-linux-glibc2.12-x86_64.tar.xz
  mv ${packages_dir}/mysql-${mysql_version}-linux-glibc2.12-x86_64.tar.xz ./
  tar xf mysql-${mysql_version}-linux-glibc2.12-x86_64.tar.xz
  rm -rf mysql-${mysql_version}-linux-glibc2.12-x86_64.tar.xz
  mv mysql-${mysql_version}-linux-glibc2.12-x86_64 mysql-${mysql_version}
  cp -r ${cwd}/deploy/fate_base/mysql/conf mysql-${mysql_version}/
  cp ${cwd}/deploy/fate_base/mysql/service.sh mysql-${mysql_version}/
  if [ $1 == "1x" ]; then
    rm -rf ${packages_dir}/sql_meta_service
    mkdir -p ${packages_dir}/sql_meta_service
    cd ${packages_dir}/sql_meta_service
    cp ${source_code_dir}/eggroll_1x/framework/meta-service/src/main/resources/create-meta-service.sql ./
  fi
  echo "[INFO] Packaging mysql done"
}

python_package() {
  rm -rf ${packages_dir}/python
  echo "[INFO] Packaging python start"
  mkdir -p ${packages_dir}/python
  cd ${packages_dir}/python
  get_module_package ${source_code_dir} "python" pip-packages-fate-${python_version}.tar.gz
  get_module_package ${source_code_dir} "python" Miniconda3-4.5.4-Linux-x86_64.sh
  mv ${packages_dir}/pip-packages-fate-${python_version}.tar.gz ./
  mv ${packages_dir}/Miniconda3-4.5.4-Linux-x86_64.sh ./
  tar xzf ./pip-packages-fate-${python_version}.tar.gz
  rm ./pip-packages-fate-${python_version}.tar.gz
  cp ${source_code_dir}/requirements.txt ./
  echo "[INFO] Packaging python done"
}
redis_package() {
  rm -rf ${packages_dir}/redis
  echo "[INFO] Packaging redis start"
  mkdir -p ${packages_dir}/redis
  cd ${packages_dir}/redis
  get_module_package ${source_code_dir} "redis" redis-${redis_version}.tar.gz
  mv ${packages_dir}/redis-${redis_version}.tar.gz ./
  tar xzf redis-${redis_version}.tar.gz
  rm -rf redis-${redis_version}.tar.gz
  cp ${cwd}/deploy/fate_base/redis/service.sh ./redis-${redis_version}
  echo "[INFO] Packaging redis done"

}

global_env_package() {
  rm -rf ${packages_dir}/global_env
  cd ${cwd}/deploy
  echo "[INFO] Packaging global_env start"
  mkdir -p ${packages_dir}/global_env
  cp services.sh init_env.sh ${packages_dir}/global_env
  cp ./fate_base/install_os_env.sh ${packages_dir}/global_env
  echo "[INFO] Packaging arch done"
}

case "$1" in
2x)
  eggroll_download $1
  fateboard_download
  config_init $1
  fate_compile $1
  eggroll_2x_package
  fateboard_package
  federatedml_package
  examples_package
  federatedrec_package
  arch_package
  fate_flow_package
  jdk_package
  mysql_package $1
  python_package
  redis_package
  global_env_package
  ;;
1x)
  eggroll_download $1
  fateboard_download
  config_init $1
  eggroll_1x_compile
  fate_compile $1
  eggroll_1x_package
  fateboard_package
  federation_package
  proxy_package
  federatedml_package
  examples_package
  federatedrec_package
  arch_package
  fate_flow_package
  jdk_package
  mysql_package $1
  python_package
  redis_package
  global_env_package
  ;;
*)
  echo "This type doesn't support! Only support 1x | 2x"
  exit
  ;;
esac

echo "[INFO] Package fate done"
echo "[INFO] A total of $(ls ${packages_dir} | wc -l | awk '{print $1}') packages:"
ls -lrt ${packages_dir}
