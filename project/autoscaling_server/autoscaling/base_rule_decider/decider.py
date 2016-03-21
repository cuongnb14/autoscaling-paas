from autoscaling.autoscaling import *
from .model import *
import logging 
import time

class BaseRuleDecider(Decider):
    """docstring for BaseRuleDecider"""
    AVG_METRICS_SERIES = "metrics"

    def __init__(self,app_id, mysql_client, influxdb_client, marathon_client):
        self.logger = logging.getLogger("BaseRuleDecider")
        self.mysql_client = mysql_client
        self.app = self.get_app(app_id)
        self.scaler = Scaler(marathon_client, app_id, self.app.min_instances, self.app.max_instances)
        self.monitor = Monitor(app_id, influxdb_client, marathon_client)
        self.influxdb_client = influxdb_client

    def get_policies(self, app_id):
        """Return all policies of app_uuid
        
        @param int app_id
        @return iter Policy
        """
        policies = self.mysql_client.query(Policy).filter_by(app_id=app_id)
        return policies

    def get_app(self, app_name):
        """Return App have name is app_name
        
        @param string app_name
        @return App 
        """
        app = self.mysql_client.query(App).filter_by(name=app_name).first()
        return app

    def apply_rule(self, policie, metrics):
        """Check rule and return number intances need scale, time wait affter scale if rule is True
        
        @param models.Policie policies
        @param dict metrics, values of metric
        @return tuple, number intances need scale and time wait affter scale
        """
        delta = {"up": 0, "down": 0}
        time_wait = {"up": 0, "down": 0}
        # Check upper_threshold
        if(metrics[policie.metric_type] > policie.upper_threshold):
            delta['up'] = policie.instances_in
            time_wait["up"] = policie.scale_up_wait
        # Check lower_threshold
        if(metrics[policie.metric_type] < policie.lower_threshold):
            delta['down'] = policie.instances_out
            time_wait["down"] = policie.scale_down_wait
        return (delta, time_wait)

    def deciding(self):
        avg_cpu_usage = self.monitor.avg_cpu_usage()
        avg_memory_usage = self.monitor.avg_memory_usage()
        metrics = {"cpu": avg_cpu_usage, "mem": avg_memory_usage}
        self.logger.info("start deciding...")
        self.logger.info("metrics: {}".format(metrics))
        data = dict()
        data['name'] = self.AVG_METRICS_SERIES
        data['columns'] = ['app_id', 'cpu', 'memory', "instances"]
        data['points'] = [[self.app.name, avg_cpu_usage, avg_memory_usage, self.monitor.get_current_instances()]]
        self.influxdb_client.write_points([data])
        instances_delta = {"up": 0, "down": 100}
        time_wait = {"up": 0, "down": 0}
        # Get instances_delta up is max and instances_delta down is min
        for policie in self.app.policies:
            (delta, time_wait_temp) = self.apply_rule(policie, metrics)
            if(instances_delta['up'] < delta['up']):
                instances_delta['up'] = delta['up']
                time_wait["up"] = time_wait_temp["up"]
            if(instances_delta['down'] > delta['down']):
                instances_delta['down'] = delta['down']
                time_wait["down"] = time_wait_temp["down"]

        if(instances_delta['up'] > 0):
            self.scaler.scale(instances_delta['up'])
            self.logger.info("Sleep: {}s".format(time_wait["up"]))
            time.sleep(time_wait["up"])
        elif(instances_delta['down'] > 0):
            self.scaler.scale(0-instances_delta['down'])
            self.logger.info("Sleep: {}s".format(time_wait["down"]))
            time.sleep(time_wait["down"])


