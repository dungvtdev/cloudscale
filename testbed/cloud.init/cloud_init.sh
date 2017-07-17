#!/bin/bash

echo "hello" > /tmp/hello

apt install -y curl
apt install -y python-falcon
sudo apt install gunicorn -y

wget https://gist.githubusercontent.com/dungvtdev/e3cc837864eb89d695a6884541d8b1e7/raw/4922befcc318066193ed771fa2732fb8c83d480d/testapp2.py

# curl -X POST -d '{"servers":[["",8000]]}' 192.168.122.1:8080/add_servers

gunicorn testapp2:app -b 0.0.0.0:8000
# python testapp2.py

echo "success init"