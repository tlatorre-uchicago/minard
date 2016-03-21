default: build

INSTALL=install

.DEFAULT:
	./setup.py $@

build:
	./setup.py build

/opt/minard/bin/activate:
	virtualenv --system-site-packages /opt/minard

install: /opt/minard/bin/activate
	/opt/minard/bin/python setup.py install
	$(INSTALL) init/gunicorn /etc/init.d/
	$(INSTALL) init/gunicorn_snoplus_log /etc/init.d/
	$(INSTALL) init/minard_dispatch_push /etc/init.d/
	$(INSTALL) init/minard_dispatch_pull /etc/init.d/
	$(INSTALL) init/orca_producer /etc/init.d/
	$(INSTALL) init/orca_consumer_cmos /etc/init.d/
	$(INSTALL) init/orca_consumer_base /etc/init.d/
	chkconfig gunicorn on
	chkconfig gunicorn_snoplus_log on
	chkconfig minard_dispatch_push on
	chkconfig minard_dispatch_pull on
	chkconfig orca_producer on
	chkconfig orca_consumer_cmos on
	chkconfig orca_consumer_base on

.PHONY: install build
