#!/bin/bash

apt-get update
apt-get install python3-pip -y
cd /vagrant/
pip3 install --upgrade pip
pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000
