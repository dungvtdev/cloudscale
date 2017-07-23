#!/bin/bash
sudo apt install python-falcon -y
sudo apt install gunicorn -y

wget -O testapp.py https://gist.githubusercontent.com/dungvtdev/872b75e1c1ec62a1477cb97885cfa4e4/raw/6bc87d4cf53b23f2798df1286cf4cc35ec68dd80/testapp.cloud.py

gunicorn testapp:app -b 0.0.0.0:8000