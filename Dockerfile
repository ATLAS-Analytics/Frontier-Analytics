FROM python:3.6
# run celery in a root mode
ENV C_FORCE_ROOT true

# create a working directory 
COPY . /celery-queue
WORKDIR /celery-queue

#install requirements for celery
RUN pip3 install -U -r requirements.txt