import sys
import os
import getpass
from django.core.management.base import BaseCommand, CommandError
from django.template import Context, Template
from django.conf import settings
from subprocess import run, PIPE


nginx_template = """
worker_processes 1;

user nobody nogroup;
# 'user nobody nobody;' for systems with 'nobody' as a group instead
pid /tmp/nginx.pid;
error_log /tmp/nginx.error.log;

events {
  worker_connections 1024; # increase if you have lots of clients
  accept_mutex off; # set to 'on' if nginx worker_processes > 1
  # 'use epoll;' to enable for Linux 2.6+
  # 'use kqueue;' to enable for FreeBSD, OSX
}

http {
  include mime.types;
  # fallback in case we can't determine a type
  default_type application/octet-stream;
  access_log /tmp/nginx.access.log combined;
  sendfile on;

  upstream app_server {
    # fail_timeout=0 means we always retry an upstream even if it failed
    # to return a good HTTP response

    # for UNIX domain socket setups
    server unix:{{app_base}}/tmp/gunicorn.sock fail_timeout=0;

  }

  server {
    # if no Host match, close the connection to prevent host spoofing
    listen 80 default_server;
    return 444;
  }

  server {
    # use 'listen 80 deferred;' for Linux
    # use 'listen 80 accept_filter=httpready;' for FreeBSD
    listen 80;
    client_max_body_size 4G;

    # set the correct host(s) for your site
    server_name {{serve_name}};

    keepalive_timeout 5;

    # path for static files
    root {{static_root}};

    location / {
      # checks for static file, if not found proxy to app
      try_files $uri @proxy_to_app;
    }

    location @proxy_to_app {
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      # enable this if and only if you use HTTPS
      # proxy_set_header X-Forwarded-Proto https;
      proxy_set_header Host $http_host;
      # we don't want nginx trying to do something clever with
      # redirects, we set the Host: header above already.
      proxy_redirect off;
      proxy_pass http://app_server;
    }

    error_page 500 502 503 504 /500.html;
    location = /500.html {
      root /path/to/app/current/public;
    }
  }
}
"""


class Command(BaseCommand):
    help = 'Build components'
    conf_name = 'nginx.bot.conf'
    app_name = 'deployment'

    def handle(self, *args, **options):
        template = Template(nginx_template)
        context = Context({
            'work_dir': settings.BASE_DIR,
            'app_base': os.path.join(settings.BASE_DIR, self.app_name),
            'server_name': ' '.join(settings.ALLOWED_HOSTS),
            'static_root': settings.STATIC_ROOT,
        })

        self.stdout.write('Generating {} ...'.format(self.conf_name))
        config_file = os.path.join(
            settings.BASE_DIR, self.conf_name
        )

        with open(config_file, 'w') as f:
            f.write(template.render(context))

        self.stdout.write(
            '{} file was created.'.format(config_file)
        )
