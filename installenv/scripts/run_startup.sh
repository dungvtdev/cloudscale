#!/bin/bash

# how to
# dang nhap tai khoan root
# crontab -e
# them dong: @reboot /root/run_startup.sh

sudo docker start influxsrv
sudo docker start cadvisor

echo $(date) >> startup.log

gunicorn testapp_cloud:app -b 0.0.0.0:8000