#!/usr/bin/env python3
from autoscaling.autoscaling import AutoScaling
from autoscaling.decider import BaseRuleDecider
from config import *
from marathon import MarathonClient
from influxdb.influxdb08 import InfluxDBClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import sys
from autoscaling.model import WebApp

def main():
    logging.basicConfig(stream=sys.stderr, level=getattr(logging, 'INFO'))
    logging.getLogger("requests.packages.urllib3.connectionpool").setLevel("ERROR")
    logging.getLogger("marathon").setLevel("ERROR")
    logger = logging.getLogger("autoscaling")

    engine = create_engine("mysql://{}:{}@{}:{}/{}".format(MYSQLDB["USERNAME"], MYSQLDB["PASSWORD"],MYSQLDB["HOST"], MYSQLDB["PORT"], MYSQLDB["DBNAME"]), encoding='utf-8', echo=False)
    Session = sessionmaker(bind=engine)

    mysql_client = Session()
    marathon_client = MarathonClient('http://'+MARATHON['HOST']+':'+MARATHON['PORT'])
    influxdb_client = InfluxDBClient(INFLUXDB["HOST"], INFLUXDB["PORT"], INFLUXDB["USERNAME"], INFLUXDB["PASSWORD"], INFLUXDB["DBNAME"])

    app_uuid = sys.argv[1]
    app = mysql_client.query(WebApp).filter_by(uuid=app_uuid).first()
    if app:
        decider = BaseRuleDecider(app, influxdb_client, marathon_client)
        logger.info("Start autoscaling: "+app_uuid)
        autoscaling = AutoScaling(decider, TIME_INTERVAL)
        autoscaling.run()
    else:
        logger.error("App uuid not found: "+app_uuid)

if __name__ == '__main__':
    main()
