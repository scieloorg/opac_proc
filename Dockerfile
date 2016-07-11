FROM python:2.7

COPY . /app

WORKDIR /app
VOLUME /app/logs

RUN pip install -r requirements.txt

CMD python am2opac.py
