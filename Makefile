default: build

.DEFAULT:
	./setup.py $@

build:
	./setup.py build

install:
	./setup.py install

.PHONY: install build
