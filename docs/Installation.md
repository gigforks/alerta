# Prerequests
```
apt-get install git mongodb-server tmux python3-pip  python3-dev nginx -y
```
# Configure mongodb
```
$ sudo vi /etc/systemd/system/mongodb.service
```

```
[Unit]
Description=High-performance, schema-free document-oriented database
After=network.target

[Service]
User=mongodb
ExecStart=/usr/bin/mongod --quiet --config /etc/mongod.conf

[Install]
WantedBy=multi-user.target
```
```
$ sudo systemctl start mongodb
$ sudo systemctl status mongodb
$ sudo systemctl enable mongodb
```
# installing Alerta
```
$ sudo apt-get install -y python-pip python-dev nginx
pip3 install git+https://github.com/gigforks/alerta.git
pip3 install alerta uwsgi
```
# To install the web console run
```
$ cd /var/www/html
$ wget -q -O - https://github.com/gigforks/angular-alerta-webui/tarball/master | sudo tar zxf -
$ sudo mv gigforks-angular-alerta-webui*/app/* .
```
# Configure wsgi
```
# Create a wsgi python file, uWsgi configuration file and systemd script:
$ sudo vi /var/www/wsgi.py
```
```
from alerta.app import app
```

```
$ sudo vi /etc/uwsgi.ini
```
```
[uwsgi]
chdir = /var/www
mount = /api=wsgi.py
callable = app
manage-script-name = true

master = true
processes = 5
logger = syslog:alertad

socket = /tmp/uwsgi.sock
chmod-socket = 664
uid = www-data
gid = www-data
vacuum = true

die-on-term = true
```
## create uwsgi systemd service
```
$ sudo vi /etc/systemd/system/uwsgi.service
```

```
[Unit]
Description=uWSGI service

[Service]
ExecStart=/usr/local/bin/uwsgi --ini /etc/uwsgi.ini

[Install]
WantedBy=multi-user.target
```

```
$ sudo systemctl start uwsgi
$ sudo systemctl status uwsgi
$ sudo systemctl enable uwsgi
```
#Configure nginx to serve Alerta as a uWsgi application on /api and the web console as static assets.
```
$ sudo vi /etc/nginx/sites-enabled/default
```

```
server {
        listen 80 default_server;
        listen [::]:80 default_server;

        location /api { try_files $uri @api; }
        location @api {
            include uwsgi_params;
            uwsgi_pass unix:/tmp/uwsgi.sock;
            proxy_set_header Host $host:$server_port;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location / {
                root /var/www/html;
        }
}
```
```
sudo service nginx restart
```


#Modify config.js
```
sudo vi /var/www/html/config.js
```
```
'use strict';

angular.module('config', [])
  .constant('config', {
    'endpoint'    : "/api",
    'provider'    : "itsyouonline", // google, github, gitlab, keycloak, saml2 or basic
    'client_id'   : "<organizaion>",
    'colors'      : {}, // use default colors
    'severity'    : {}, // use default severity codes
    'audio'       : {}, // no audio
    'tracking_id' : ""  // Google Analytics tracking ID eg. UA-NNNNNN-N
  });
```
# Create SECRET_KEY
```
$ cat /dev/urandom | tr -dc A-Za-z0-9_\!\@\#\$\%\^\&\*\(\)-+= | head -c 32 && echo
```
Assign the random string to the SECRET_KEY sever setting:
```
$ vi /etc/alertad.conf
SECRET_KEY='<INSERT_RANDOM_STRING>'
```
# Configure /etc/alertad.conf
```
sudo vi /etc/alertad.conf
```
```
SECRET_KEY='f7v%@!(TNBl=DQE4Iag)Hh9G_t40@HTJ'
SEVERITY_MAP = {
    'critical': 1,
    'warning': 4,
    'indeterminate': 5,
    'ok': 5,
    'unknown': 9,
}
AUTH_REQUIRED = True
PLUGINS=['gig']
ALLOWED_ENVIRONMENTS=['Production', 'Development', 'Code']
DEBUG=True
FLASK_API_URL="http://localhost:5000/alerts"
ITSYOUONLINE_CLIENT_SECRET ="jSeT43WRv-kb0oJdsmRSguCDMsZwHG0TBxX53RYKflFYODNVYJvn"
ADMIN_USERS=['ashraf']
```
