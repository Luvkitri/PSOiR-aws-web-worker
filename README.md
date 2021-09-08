# PSOiR-aws-web-worker
Web worker for receiving and doing 'work' on messages from clients

## AWS EC2 Script
#! /bin/bash

 apt-get -y update
 apt-get -y install nodejs npm git
 git clone https://github.com/Luvkitri/PSOiR-aws-web-worker.git
 cd /PSOiR-aws-web-worker
 cd /config
 cp .env.example .env
 cd ..
 npm install
 npm start
