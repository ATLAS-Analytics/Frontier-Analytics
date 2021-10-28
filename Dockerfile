FROM centos

# Run update
# gcc because we need regex and pyldap
# openldap-devel because we need pyldap
RUN yum update -y && \
       # yum install -y https://centos7.iuscommunity.org/ius-release.rpm && \
       # yum install -y python36u python36u-libs python36u-devel python36u-pip
       dnf install -y python3

# pipenv installation
RUN pip3.6 install pipenv
# RUN ln -s /usr/bin/pip3.6 /bin/pip3

# python must be pointing to python3.6
# RUN ln -s /usr/bin/python3.6 /usr/bin/python3

# Java OpenJDK
RUN yum install -y \
       java-1.8.0-openjdk \
       java-1.8.0-openjdk-devel
ENV JAVA_HOME /etc/alternatives/jre
#install git wget
RUN yum -y install wget git

#create a workspace 
COPY . /workdir
WORKDIR /workdir
# prepare spark directory 
RUN mkdir /workdir/spark && chown 755 /workdir/spark

# Spark dependencies
ENV APACHE_SPARK_VERSION 2.4.8
ENV HADOOP_VERSION 2.7

# https://www-eu.apache.org/dist/spark/spark-2.4.2/spark-2.4.2-bin-hadoop2.7.tgz
RUN cd /tmp && wget -q https://www-eu.apache.org/dist/spark/spark-${APACHE_SPARK_VERSION}/spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
       tar xzf spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -C /workdir/spark && \
       rm spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz
RUN cd /usr/local && ln -s spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} spark
ENV SPARK_HOME /workdir/spark/spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}

# Python packages
RUN pip3 install -U pip && pip3 install --no-cache-dir six pytest numpy cython 

#install analytics packages
RUN pip3 install -r /workdir/requirements.txt
