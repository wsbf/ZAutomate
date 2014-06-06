.PHONY: all

VENVNAME=ZA
PYTHONVERSION=2.7.2
BASE=~/.pythonbrew/venvs/

PREFIX = $(BASE)Python-$(PYTHONVERSION)/$(VENVNAME)

all:
	make init_cache
	make snack
	make libmad
	make pymad
	make libao
	make pyao

init_cache:
	-mkdir -p cached
	-wget -nc -O cached/snack2.2.9-osx.tar.gz http://www.speech.kth.se/snack/dist/snack2.2.9-osx.tar.gz
	-wget -nc -O cached/libmad-0.15.1b.tar.gz ftp://ftp.mars.org/pub/mpeg/libmad-0.15.1b.tar.gz
	-wget -nc -O cached/libmad-0.15.1b-fixes-1.patch http://www.linuxfromscratch.org/patches/blfs/svn/libmad-0.15.1b-fixes-1.patch
	-wget -nc -O cached/pymad-0.6.tar.gz http://spacepants.org/src/pymad/download/pymad-0.6.tar.gz
	-wget -nc -O cached/libao-1.2.0.tar.gz http://downloads.xiph.org/releases/ao/libao-1.2.0.tar.gz
	-wget -nc -O cached/pyao_0.82.orig.tar.gz http://ftp.de.debian.org/debian/pool/main/p/pyao/pyao_0.82.orig.tar.gz
	-wget -nc -O cached/pyao_0.82-3.diff.gz http://ftp.de.debian.org/debian/pool/main/p/pyao/pyao_0.82-3.diff.gz
	@echo "Dependency cache filled"

snack: cached/snack2.2.9-osx.tar.gz
	@echo Installing tkSnack
	tar xfz cached/snack2.2.9-osx.tar.gz
	cd snack2.2/python && python setup.py install
	rm -rf snack2.2

libmad: cached/libmad-0.15.1b.tar.gz cached/libmad-0.15.1b-fixes-1.patch
	@echo Installing libmad into $(PREFIX)
	tar xfz cached/libmad-0.15.1b.tar.gz
	patch -p 0 < cached/libmad-0.15.1b-fixes-1.patch
	cd libmad-0.15.1b && ./configure --prefix $(PREFIX)
	cd libmad-0.15.1b && make && make install
	rm -rf libmad-0.15.1b

pymad: cached/pymad-0.6.tar.gz
	@echo Installing pymad into $(PREFIX)
	tar xfz cached/pymad-0.6.tar.gz
	cd pymad-0.6 && python config_unix.py --prefix $(PREFIX)
	cd pymad-0.6 && python setup.py install
	rm -rf pymad-0.6

libao: cached/libao-1.2.0.tar.gz
	@echo Installing libao into $(PREFIX)
	tar xfz cached/libao-1.2.0.tar.gz
	cd libao-1.2.0 && ./configure --prefix $(PREFIX)
	cd libao-1.2.0 && make && make install
	rm -rf libao-1.2.0

pyao: cached/pyao_0.82.orig.tar.gz cached/pyao_0.82-3.diff.gz
	tar xfz cached/pyao_0.82.orig.tar.gz
	gzcat cached/pyao_0.82-3.diff.gz > cached/pyao_0.82-3.diff
	patch -p 0 < cached/pyao_0.82-3.diff
	cd pyao-0.82 && python config_unix.py --prefix $(PREFIX)
	cd pyao-0.82 && python setup.py install
	rm -rf pyao-0.82
