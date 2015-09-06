#!/bin/bash

apt-get remove -y grub-pc
apt-get update
apt-get upgrade -y
apt-get install -y git libpq-dev python-dev python-pip memcached

pip install virtualenv
virtualenv /home/vagrant/MainSite
source /home/vagrant/MainSite/bin/activate
echo source /home/vagrant/MainSite/bin/activate >> /home/vagrant/.profile

pip install -r /vagrant/requirements.txt
