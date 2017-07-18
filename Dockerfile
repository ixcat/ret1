FROM mysql

# merge of mysql, datajoint/mysql-docker and datajoint/pydev-docker + demo
# initial build OK, awaiting build verify/git integ tests

RUN apt-get update &&\
	apt-get install -y build-essential \
		gfortran \
		nvi \
		curl \
		wget \
		zip \
		zlib1g-dev \
		unzip \
		libfreetype6-dev \
		pkg-config \
		libblas-dev \
		liblapack-dev \
		python3-dev \
		python3-pip \
		python3-tk \
		python3-wheel \
		swig \
		cython \
		git &&\
	pip3 install datajoint ipython

ARG GITREV=default
RUN GITREV=${GITREV} git clone https://github.com/ixcat/ret1 \
	&& cd ret1 && git pull \
	&& python3 ./setup.py build install

ADD mysqld.cnf /etc/mysql/mysql.conf.d/mysqld.cnf
ADD test-driver.sh /usr/local/bin/test-driver.sh

CMD ["/bin/sh", "-c", "ipython"]
