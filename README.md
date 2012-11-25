``` This is a project deep in development, not yet ready for production use ```

Reconfigure is an ORM for your config files. Direct translation of file into a Python objects and back makes it easy to do any kind of reconfiguration.
You can even extend reconfigure with your own classes for your custom configuration files!

Quick example:

```
>>> from reconfigure.configs import FSTabConfig
>>> from reconfigure.builders.fstab import FilesystemBuilder
>>> config = FSTabConfig(path='/etc/fstab')
>>> config.load()
>>> print config.tree
{
    filesystems [
        {
            type proc
            device proc
            mountpoint /proc
            freq 0
            passno 0
            options nodev,noexec,nosuid
        }, 
        {
            type ext4
            device UUID=83810b56-ef4b-44de-85c8-58dc589aef48
            mountpoint /
            freq 0
            passno 1
            options errors=remount-ro
        }
    ]
}
>>> config.tree.filesystems[1].device = '/dev/sda1'
>>> fs = FilesystemBuilder.empty()
>>> fs.device = '/dev/sdb1'
>>> fs.mountpoint = '/mnt/temp'
>>> config.tree.filesystems.append(fs)
>>> config.save()
>>> print open('/etc/fstab').read()
proc    /proc   proc    nodev,noexec,nosuid     0       0
/dev/sda1       /       ext4    errors=remount-ro       0       1
/dev/sdb1       /mnt/temp   none none none none
```

### Config support so far

* /etc/fstab
* /etc/resolv.conf
* /etc/hosts
* (Ajenti)[http://ajenti.org]
* nginx

### How it works

The processing chain consists of three main components:

#### Parser

The parser transforms the raw text config into a Node Tree, which only represents structure of the config file. This is awfully similar to Abstract Syntax Trees.
Example:
```
>>> from reconfigure.parsers import NginxParser
>>> parser = NginxParser()
>>> content = open('/etc/nginx/nginx.conf').read()
>>> print content 
user www-data;
worker_processes 4;
pid /var/run/nginx.pid;

events {
        worker_connections 768;
}

http {
        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;
        keepalive_timeout 65;
        types_hash_max_size 2048;
        include /etc/nginx/mime.types;
        default_type application/octet-stream;
        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;
        gzip on;
        gzip_disable "msie6";
        include /etc/nginx/conf.d/*.conf;
        include /etc/nginx/sites-enabled/*;
}

>>> print pparser.parse(content)
(None)
        user = www-data
        worker_processes = 4
        pid = /var/run/nginx.pid
        (events)
                worker_connections = 768
        (http)
                sendfile = on
                tcp_nopush = on
                tcp_nodelay = on
                keepalive_timeout = 65
                types_hash_max_size = 2048
                include = /etc/nginx/mime.types
                default_type = application/octet-stream
                access_log = /var/log/nginx/access.log
                error_log = /var/log/nginx/error.log
                gzip = on
                gzip_disable = "msie6"
                include = /etc/nginx/conf.d/*.conf
                include = /etc/nginx/sites-enabled/*

The Node Trees have the same format for every config, so Parsers abstract us away from the file format.

#### Includer
