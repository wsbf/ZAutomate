snack:
	wget http://www.speech.kth.se/snack/dist/snack2.2.9-osx.tar.gz
	tar xfz snack2.2.9-osx.tar.gz
	cd snack2.2/python && python setup.py install
	rm -rf snack2.2
	rm snack2.2.9-osx.tar.gz


all: snack 
