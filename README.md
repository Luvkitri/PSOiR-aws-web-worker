# PSOiR-aws-web-worker
Web worker for receiving and doing 'work' on messages from clients

## AWS EC2 Script
#! /bin/bash

apt-get -y update \
apt-get -y install python git \
git clone https://github.com/Luvkitri/PSOiR-aws-web-worker.git \
cd /PSOiR-aws-web-worker/ \
pip install --user pipenv \
pipenv install \
pipenv run python app.py \
