FROM atlasanalyticsservice/frontier_analytics_base

ARG CERN_USER
ARG CERN_PASS

RUN groupadd -r frntmon -g 1000 && useradd -u 1000 -r -g frntmon -m -d /home/frntmon -s /sbin/nologin -c "Frontier user" frntmon && chmod 755 /home/frntmon

ENV USR frntmon
WORKDIR /home/${USR}/celery-queue
COPY . /home/${USR}/celery-queue
RUN mkdir /home/${USR}/celery-queue/Files
RUN chown -R ${USR}:${USR} /home/${USR}
RUN chmod 755 /home/${USR}/celery-queue

RUN pip3 install --no-cache-dir "git+https://${CERN_USER}:${CERN_PASS}@gitlab.cern.ch/formica/coolR.git#egg=coolr&subdirectory=coolR-client/python"

ENTRYPOINT celery -A celery_tasks worker --loglevel=info --uid 1000