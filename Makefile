.PHONY: all

all:
	make init_cache
	make snack
	make pyao

init_cache:
	-mkdir -p cached
	-wget -nc -O cached/snack2.2.9-osx.tar.gz http://www.speech.kth.se/snack/dist/snack2.2.9-osx.tar.gz
	-wget -nc -O cached/pyao_0.82.orig.tar.gz http://ftp.de.debian.org/debian/pool/main/p/pyao/pyao_0.82.orig.tar.gz
	-wget -nc -O cached/pyao_0.82-3.diff.gz http://ftp.de.debian.org/debian/pool/main/p/pyao/pyao_0.82-3.diff.gz
	@echo "Dependency cache filled"

snack: cached/snack2.2.9-osx.tar.gz
	tar xfz cached/snack2.2.9-osx.tar.gz
	cd snack2.2/python && python setup.py install
	rm -rf snack2.2

pyao: cached/pyao_0.82.orig.tar.gz cached/pyao_0.82-3.diff.gz
	tar xfz cached/pyao_0.82.orig.tar.gz
	gzcat cached/pyao_0.82-3.diff.gz > pyao_0.82-3.diff
	patch -p 0 < pyao_0.82-3.diff
	cd pyao-0.82 && python config_unix.py
	cd pyao-0.82 && python setup.py install
	rm -rf pyao-0.82
