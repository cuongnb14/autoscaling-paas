#!/usr/bin/env python3
__author__ = 'cuongnb14@gmail.com'
""" Script for mapping docker container name with mesos task id in mesosphere system """

import time
import logging
import sys
import os

from docker import Client
from influxdb.influxdb08 import InfluxDBClient
from configs import *
from apscheduler.schedulers.background import BlockingScheduler

logger = logging.getLogger('mapping_docker_mesos')
logging.basicConfig(stream=sys.stderr, level=getattr(logging, 'INFO'))

docker_client = Client(base_url='unix://var/run/docker.sock')
influxdb_client = InfluxDBClient(
        host=INFLUXDB['HOST'],
        port=INFLUXDB['PORT'],
        username=INFLUXDB['USER'],
        password=INFLUXDB['PASS'],
        database=INFLUXDB['DBNAME']
    )

def mapping():
    """Mapping docker container name with mesos task id 
    
    @return list, list mapped [container-name, mesos-task-id]
    """
    containers = docker_client.containers()
    mapping_list = list()
    for container in containers:
        if container['Names'][0].startswith('/mesos-'):
            logger.debug("Mapping container name: "+container['Names'][0])
            dockerid_mapping_mesosid = list()
            dockerid_mapping_mesosid.append(container['Names'][0][1:])
            container_env = docker_client.inspect_container(container['Id'])['Config']['Env']
            for env in container_env:
                if env.startswith('MESOS_TASK_ID'):
                    dockerid_mapping_mesosid.append(env.split('=')[1])
                    logger.debug("mapping with "+env.split('=')[1])
                    mapping_list.append(dockerid_mapping_mesosid)
                    break
    return mapping_list


def update_mapping():
    """Update list mapped to database"""
    try:
        logger.info("mapping...")
        mapping_list = mapping()
        logger.info(mapping_list)
        data = dict()
        data['name'] = INFLUXDB["SERIES"]
        data['columns'] = ['container_name', 'mesos_task_id']
        data['points'] = [t for t in mapping_list]
        logger.info("update database...")
        influxdb_client.write_points([data])
    except Exception as e:
        logger.error(e)
    

def main():
    logging.getLogger("apscheduler.executors.default").setLevel("ERROR") 
    scheduler = BlockingScheduler()
    scheduler.add_job(update_mapping, 'interval', seconds=TIME_INTERVAL)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main()
