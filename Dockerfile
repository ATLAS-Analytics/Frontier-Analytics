FROM atlasanalyticsservice/frontier_base

ARG CERN_USER
ARG CERN_PASS

# Add the user UID:1000, GID:1000, home at /app
# RUN groupadd -r frntmon -g 1000 && useradd -u 1000 -r -g frntmon -m -d /home/frntmon -s /sbin/nologin -c "Frontier user" frntmon && chmod 755 /home/frntmon

# set up environment variables
# ENV USR frntmon
RUN mkdir /app
WORKDIR /app

# Python packages
RUN pip3 install --no-cache-dir "git+https://${CERN_USER}:${CERN_PASS}@gitlab.cern.ch/formica/coolR.git#egg=coolr&subdirectory=coolR-client/python"

# # install analytics packages
# COPY Analytics /home/${USR}/Analytics

# # copy templates and static files into the workDIR
# COPY templates /home/${USR}/templates
# COPY static /home/${USR}/static
# COPY ./worker.py /home/${USR}/
# COPY FrontierAnalyticsApp.py  /home/${USR}/


COPY Analytics /app/
COPY templates /app/templates
COPY static /app/static
COPY ./worker.py /app
COPY FrontierAnalyticsApp.py  /app

ENV C_FORCE_ROOT true
ENV HOST 0.0.0.0
ENV PORT 5000
ENV DEBUG true

ENV PYTHONPATH ${SPARK_HOME}/python:${SPARK_HOME}/python/lib/py4j-0.10.7-src.zip:${PYTHONPATH}
EXPOSE 5000
CMD ["python3", "/app/FrontierAnalyticsApp.py"]











