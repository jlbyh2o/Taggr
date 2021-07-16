# Taggr

Taggr is a Flask application that allows users to print Dymo labels from data in Square.

## Installation

Instructions to install on Ubuntu Server 20.04 with Nginx and Supervisor.

### System Packages
```console
sudo apt install glabels nginx supervisor python3.8-venv cups
```

### Create Directory
```console
sudo mkdir /opt/Taggr
sudo chmod -R a+rw /opt/Taggr
cd /opt/Taggr
```

### Install Taggr
```console
git clone https://github.com/jlbyh2o/Taggr.git .
```

### Create and Activate a new Python Virtual Environment
```console
python3 -m venv venv
source venv/bin/activate
```

### Install Flask and Dependencies
```console
pip install -r requirements.txt
```

### Initialize the Database
```console
export FLASK_APP=taggr
flask db upgrade
```

### Configure the Secret Key
```console
python -c 'import os; print("SECRET_KEY = " + str(os.urandom(16)))' > instance/config.py
```

### Install Gunicorn
```console
pip install gunicorn
```

## Setup Supervisor
Create a supervisor file in /etc/supervisor/conf.d/ and configure it.
```console
sudo nano /etc/supervisor/conf.d/taggr.conf
```
Paste the following into /etc/supervisor/conf.d/taggr.conf
```roboconf
[program:taggr]
directory=/opt/Taggr
command=/opt/Taggr/venv/bin/gunicorn -w 4 -b localhost:8000 "taggr:app"
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/taggr.err.log
stdout_logfile=/var/log/taggr.out.log
```
### Enable the Supervisor Configuration
```console
sudo supervisorctl reread
sudo service supervisor restart
```
Check the status of supervisor
```console
sudo supervisorctl status
```
## Setup Nginx
Define a server block for Taggr.
```console
sudo nano /etc/nginx/sites-available/taggr
```
Paste the following into /etc/nginx/sites-available/taggr
```nginx
server {
    listen       80;
    server_name  taggr.local;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```
### Remove Default Site and Enable Taggr
```console
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/taggr /etc/nginx/sites-enabled/taggr
```
Restart the nginx web server.
```console
sudo nginx -t
sudo service nginx restart
```
## First-time Setup
1. Register your account by opening the Taggr website at http://taggr.local/auth/register (be sure to replace taggr.local with you own server name or IP address.)
2. Log in with your new credentials.
3. Open Settings by clicking top right dropdown.
4. Set your Square API Key and Dymo Printer.

 You are now ready to use Taggr.

## Updating
```console
cd /opt/Taggr
source venv/bin/activate
sudo supervisorctl stop taggr
git pull
flask db upgrade
sudo supervisorctl start taggr
```

## License
[Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0)
