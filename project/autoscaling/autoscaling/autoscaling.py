__author__ = 'cuongnb14@gmail.com'

import abc

from marathon import MarathonClient
import time
import logging
from influxdb.influxdb08 import InfluxDBClient
from apscheduler.schedulers.background import BlockingScheduler

class Decider(object):
    """Base Diceder"""
    __metaclass__  = abc.ABCMeta

    @abc.abstractmethod
    def deciding(self):
        """base"""

class AutoScaling(object):
    """docstring for AutoScaling"""
    def __init__(self, decider, interval):
        self.decider = decider
        self.interval = interval

    def run(self):
        while True:
            try:
                self.decider.deciding()
                time.sleep(self.interval)
            except (KeyboardInterrupt, SystemExit):
                break
            except Exception as e:
                pass
