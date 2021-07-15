# Taggr

Taggr is a Flask application that allows users to print Dymo labels from data in Square.

## Installation

Instructions to install on Ubuntu Server 20.04 with Nginx and Supervisor.

### System Packages
```shell
$ sudo apt install glabels nginx supervisor python3.8-venv
```

### Create Directory and Virtual Environment
```shell
$ sudo mkdir /opt/Taggr
$ sudo chmod -R a+rw /opt/Taggr
$ cd /opt/Taggr
$ python3 -m venv venv
```

### Activate the new Python Virtual Environment
```shell
$ source venv/bin/activate
```

### Install Wheel
```shell
$ pip install wheel
```

### Install Taggr
```shell
$ pip install taggr-<version>-py3-none-any.whl
```

### Initialize the Database
```shell
$ export FLASK_APP=taggr
$ flask init-db
```

### Configure the Secret Key
```shell
$ python -c 'import os; print("SECRET_KEY = " + str(os.urandom(16)))' > venv/var/taggr-instance/config.py
```

### Install Gunicorn
```shell
$ pip install gunicorn
```

## Setup Supervisor
Create a supervisor file in /etc/supervisor/conf.d/ and configure it.
```shell
$ sudo nano /etc/supervisor/conf.d/taggr.conf
```
Paste the following into /etc/supervisor/conf.d/taggr.conf
```roboconf
[program:taggr]
directory=/opt/Taggr
command=/opt/Taggr/venv/bin/gunicorn -w 4 -b localhost:8000 "taggr:create_app()"
autostart=true
autorestart=true
stderr_logfile=/var/log/taggr.err.log
stdout_logfile=/var/log/taggr.out.log
```
### Enable the Supervisor Configuration
```shell
$ sudo supervisorctl reread
$ sudo service supervisor restart
```
Check the status of supervisor
```shell
$ sudo supervisorctl status
```
## Setup Nginx
Define a server block for Taggr.
```shell
$ sudo nano /etc/nginx/sites-available/taggr.conf
```
Paste the following into /etc/nginx/sites-available/taggr.conf
```nginx
server {
    listen       80;
    server_name  taggr.local;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```
Restart the nginx web server.
```shell
$ sudo nginx -t
$ sudo service nginx restart
```