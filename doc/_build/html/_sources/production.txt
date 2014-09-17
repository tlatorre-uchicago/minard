Production Install
==================

To install minard for production use, first run the INSTALL script::

    git clone git@github.com/snoplus/minard
    cd minard
    sudo ./INSTALL

The INSTALL script will:

    * install redis in `/usr/local`
    * create a virtual environment in `/opt/minard`
    * install/update minard
    * install/update disp
    * create users `gunicorn`, `snoplusmon`, `nginx`
    * set up init scripts and configuration files for gunicorn, redis, and nginx


To open the redis port for the L2 process on the buffer machine::

    $ sudo iptables -I INPUT -p tcp --dport 6379 -s buffer1.sp.snolab.ca -j ACCEPT
    $ sudo iptables -I INPUT -p tcp --dport 6379 -s buffer2.sp.snolab.ca -j ACCEPT

and then to save them (on RedHat distributions)::

    $ sudo /sbin/service iptables save
