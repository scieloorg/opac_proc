FROM python:2.7
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive
# Build-time metadata as defined at http://label-schema.org
ARG OPAC_PROC_BUILD_DATE
ARG OPAC_PROC_VCS_REF
ARG OPAC_PROC_WEBAPP_VERSION

ENV OPAC_PROC_BUILD_DATE ${OPAC_PROC_BUILD_DATE}
ENV OPAC_PROC_VCS_REF ${OPAC_PROC_VCS_REF}
ENV OPAC_PROC_WEBAPP_VERSION ${OPAC_PROC_WEBAPP_VERSION}

LABEL org.label-schema.build-date=$OPAC_PROC_BUILD_DATE \
      org.label-schema.name="OPAC Proc - development build" \
      org.label-schema.description="OPAC Proc main app" \
      org.label-schema.url="https://github.com/scieloorg/opac_proc/" \
      org.label-schema.vcs-ref=$OPAC_PROC_VCS_REF \
      org.label-schema.vcs-url="https://github.com/scieloorg/opac_proc/" \
      org.label-schema.vendor="SciELO" \
      org.label-schema.version=$OPAC_PROC_WEBAPP_VERSION \
      org.label-schema.schema-version="1.0"

RUN apt-get update \
    && apt-get install -qqy --no-install-recommends apt-utils libxml2-utils \
    && rm -rf /var/lib/apt/lists/*

# COPY ./requirements.txt /app/requirements.txt
COPY . /app
RUN pip --no-cache-dir install --upgrade pip
RUN pip --no-cache-dir install -r /app/requirements.txt

COPY ./start_worker.sh /start_worker.sh
COPY ./start_scheduler.sh /start_scheduler.sh

RUN sed -i 's/\r//' /start_worker.sh \
    && sed -i 's/\r//' /start_scheduler.sh \
    && chmod +x /start_worker.sh \
    && chmod +x /start_scheduler.sh \
    && chmod -R +x /src/ \
    && chown nobody /start_worker.sh \
    && chown nobody /start_scheduler.sh \
    && chown -R nobody /src/

RUN chown -R nobody:nogroup /app
USER nobody

EXPOSE 8000
WORKDIR /app

CMD gunicorn -k gevent --workers 3 --bind 0.0.0.0:8000 webapp:app --chdir=opac_proc/web/ --log-level INFO
