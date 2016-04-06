FROM python:3.3-alpine

COPY collector.py /collector.py
COPY requirements.txt /requirements.txt

RUN pip3 install -r /requirements.txt
ENV INFLUXDB_HOST 10.10.10.51
ENV INFLUXDB_PORT 31101
ENV INFLUXDB_USERNAME root
ENV INFLUXDB_PASSWORD root
ENV INFLUXDB_DBNAME autoscaling
ENV INFLUXDB_SERIES monitoring
ENV COLLECT_TIME_INTERVAL 3
ENV BATH_TIME_INTERVAL 10

CMD ["python3","/collector.py"]
