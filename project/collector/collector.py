#! /usr/bin/env python3
from docker import Client, errors
import math
import os
import logging
import sys
import time
import concurrent.futures
from datetime import datetime
import logging
from influxdb.influxdb08 import InfluxDBClient
import signal


class Collector:

    def __init__(self):
        self.logger = logging.getLogger("Monitor")
        self.INFLUXDB = {}
        self.INFLUXDB['HOST'] = os.getenv("INFLUXDB_HOST","localhost")
        self.INFLUXDB['PORT'] = os.getenv("INFLUXDB_PORT","8086")
        self.INFLUXDB['USERNAME'] = os.getenv("INFLUXDB_USERNAME","root")
        self.INFLUXDB['PASSWORD'] = os.getenv("INFLUXDB_PASSWORD","root")
        self.INFLUXDB['DBNAME'] = os.getenv("INFLUXDB_DBNAME","autoscaling")
        self.INFLUXDB['SERIES'] = os.getenv("INFLUXDB_SERIES","monitoring")
        self.COLLECT_TIME_INTERVAL = int(os.getenv("COLLECT_TIME_INTERVAL","3"))
        self.BATH_TIME_INTERVAL = int(os.getenv("BATH_TIME_INTERVAL","10"))

        self.influxdb_client = InfluxDBClient(
            host=self.INFLUXDB['HOST'],
            port=self.INFLUXDB['PORT'],
            username=self.INFLUXDB['USERNAME'],
            password=self.INFLUXDB['PASSWORD'],
            database=self.INFLUXDB['DBNAME']
        )

        self.docker_client = Client(base_url='unix://var/run/docker.sock')
        self.data_bath = []
        self.current_data = 0

    def collecting(self, container_id):
        mesos_task_id = ""
        app_name = ""
        container_envs = self.docker_client.inspect_container(container_id)['Config']['Env']
        container_cpushares = self.docker_client.inspect_container(container_id)['HostConfig']['CpuShares'] / 1024
        for env in container_envs:
            if env.startswith('MESOS_TASK_ID'):
                mesos_task_id = env.split('=')[1]
                index = mesos_task_id.rfind('.')
                app_name = mesos_task_id[:index]
                break
        while True:
            try:
                stat = self.docker_client.stats(container_id, decode="utf8", stream=False)
                cpu_usage = (stat["cpu_stats"]["cpu_usage"]["total_usage"] - stat["precpu_stats"]["cpu_usage"]["total_usage"])
                cpu_usage = cpu_usage / container_cpushares * 100 / math.pow(10,9)
                mem_usage = stat["memory_stats"]["usage"] / stat["memory_stats"]["limit"] * 100
                current_time = datetime.now().timestamp()
                data = [current_time, container_id, app_name, mesos_task_id, cpu_usage, mem_usage]
                self.logger.debug("Append: "+str(data))
                self.data_bath.append(data)
                time.sleep(self.COLLECT_TIME_INTERVAL)
            except errors.NotFound as e:
                self.logger.info("Container {} has gone away".format(container_id))
                break
            except Exception as e:
                self.logger.error("Error "+str(e))
                break


    def send_data(self):
        while True:
            try:
                time.sleep(self.BATH_TIME_INTERVAL)
                if self.data_bath:
                    data = dict()
                    data['name'] = self.INFLUXDB["SERIES"]
                    data['columns'] = ['time', 'container_id', 'app_uuid', 'mesos_task_id', "cpu_usage", "mem_usage"]
                    data['points'] = self.data_bath
                    self.data_bath = []
                    self.logger.info("Send data ...")
                    self.logger.debug(str(data))
                    self.influxdb_client.write_points([data])
            except Exception as e:
                self.logger.error("Error "+str(e))



    def run(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            executor.submit(self.send_data)
            containers = self.docker_client.containers()
            collectors = {}
            for container in containers:
                collectors[container["Id"]] = executor.submit(self.collecting, container["Id"])
            events = self.docker_client.events(decode=True)

            for event in events:
                if event["status"] == "start":
                    self.logger.info("Start collector for: "+event["id"])
                    collectors[event["id"]] = executor.submit(self.collecting, event["id"])
                elif event["status"] == "die":
                    try:
                        self.logger.info("Cancel collector for: "+event["id"])
                        collectors[event["id"]].cancel()
                    except Exception as e:
                        self.logger.debug("Exception when Cancel collector: {} : {}".format(str(e), event["id"]))

def handler(signum=None, frame=None):
    logger.info('Signal handler called with signal {}'.format(signum))
    logger.info('Stop docker_mapping_service')
    sys.exit()

def main():
    for sign in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
        signal.signal(sign, handler)

    logging.getLogger("Collector").setLevel("DEBUG")
    logging.basicConfig(stream=sys.stdout, level="DEBUG")
    logging.getLogger("requests.packages.urllib3.connectionpool").setLevel("ERROR")
    logging.getLogger("urllib3.connectionpool").setLevel("ERROR")
    collector = Collector()
    collector.run()

if __name__ == '__main__':
    main()
