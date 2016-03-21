__author__ = 'cuongnb14@gmail.com'

import abc

from marathon import MarathonClient
import time
import logging
from influxdb.influxdb08 import InfluxDBClient
from apscheduler.schedulers.background import BlockingScheduler

class Scaler(object):
    """docstring for ClassName"""
    def __init__(self, marathon_client, app_id, min_instances, max_instances):
        self.logger = logging.getLogger("Scaler")
        self.marathon_client = marathon_client
        self.app_id = app_id
        self.min_instances = min_instances
        self.max_instances = max_instances

    def scale(self, delta):
        """sacle app_name (add or remove) delta intances
        
        @param int delta number intances add if (delta > 0) or remove if (delta < 0)
        """
        current_instances = self.marathon_client.get_app(self.app_id).instances
        new_instance = current_instances + delta
        if(new_instance > self.max_instances):
            new_instance = self.max_instances
        if(new_instance < self.min_instances):
            new_instance = self.min_instances
        if(new_instance != current_instances):
            self.logger.info("scale to: %d", new_instance)
            self.marathon_client.scale_app(self.app_id, new_instance)
        else:
            self.logger.info("number instances to threshold, no scale!")
 


class Monitor(object):
    """docstring for Moniter"""
    def __init__(self, app_id, influxdb_client, marathon_client):
       self.influxdb_client = influxdb_client
       self.marathon_client = marathon_client
       self.app = marathon_client.get_app(app_id)

    def __get_container_name(self, mesos_task_id):
        """Return container name mapping with mesos_task_id in messos
        
        @param string mesos_task_id
        """
        query = "select container_name from mappings where time>now() - 5m and mesos_task_id = '{}' limit 1".format(mesos_task_id)
        result = self.influxdb_client.query(query)
        points = result[0]["points"]
        return points[0][2]

    def get_containers_name(self):
        """Return list all containers name of application self.app
        
        @return list<string>, all containers name of self.app
        """
        tasks = self.marathon_client.list_tasks(self.app.id)   
        containers_name = []
        for task in tasks:
            containers_name.append(self.__get_container_name(task.id))
        return containers_name

    def avg_memory_usage(self):
        """Return avg memmory usage of all containers of self.app
        
        @return float, avg memmory usage
        """
        containers_name = self.get_containers_name()
        number_container = len(containers_name)
        containers_name = ["'"+x+"'" for x in containers_name]
        containers_name = ",".join(containers_name)
        query = "select memory_usage,container_name from stats where  time > now()-5m and  container_name in ({})  limit {}".format(containers_name, str(number_container*2))
        result = self.influxdb_client.query(query)
        points = result[0]["points"]
        sum_memory_usage = 0
        for point in points:
            if(point[3] != None):
                sum_memory_usage += point[3]/(self.app.mem*1048576)*100
        return sum_memory_usage / number_container

    def avg_cpu_usage(self):
        """Return avg cpu usage of all containers of self.app
        
        @return float, avg cpu usage
        """
        containers_name = self.get_containers_name()
        number_container = len(containers_name)
        containers_name = ["'"+x+"'" for x in containers_name]
        containers_name = ",".join(containers_name)
        query = "select DERIVATIVE(cpu_cumulative_usage)  as cpu_usage,container_name from stats where  time > now()-5m and  container_name in ({}) group by time(10s),container_name limit {}".format(containers_name, str(number_container))
        result = self.influxdb_client.query(query)
        points = result[0]["points"]
        sum_cpu_usage = 0
        for point in points:
            sum_cpu_usage += point[1]/1000000000/self.app.cpus*100
        return sum_cpu_usage / number_container

    def get_current_instances(self):
        return self.marathon_client.get_app(self.app.id).instances




class Decider(object):
    """Base Diceder"""
    __metaclass__  = abc.ABCMeta

    # def __init__(self,app_id, influxdb_client, marathon_client):
    #    self.scaler = Scaler(marathon_client, app_id)
    #    self.moniter = Moniter(app_id, influxdb_client, marathon_client)

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
            # except Exception as e:
            #     pass
            
     







        
        