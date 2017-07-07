#!/bin/bash

wget https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana_4.4.1_amd64.deb
apt install -y adduser libfontconfig
dpkg -i grafana_4.4.1_amd64.deb

service grafana-server start

update-rc.d grafana-server defaults