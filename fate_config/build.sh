
# copy service conf
mkdir -p fate_config/conf
cp ../conf/service_conf.yaml fate_config/conf/service_conf.yaml
cp ../fate.env fate_config/conf/fate.env
poetry build
rm -rf fate_config/conf