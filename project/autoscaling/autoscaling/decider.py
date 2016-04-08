from .autoscaling import *
from .model import *
from .scaler import Scaler
from .monitor import Monitor
import logging
import time

class BaseRuleDecider(Decider):
    """docstring for BaseRuleDecider"""

    def __init__(self,app, influxdb_client, marathon_client):
        """init

        @param model.WebApp app
        """
        self.logger = logging.getLogger("BaseRuleDecider")
        self.app = app
        self.scaler = Scaler(marathon_client, app)
        self.monitor = Monitor(influxdb_client, app)

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
        self.logger.info("start deciding...")
        metrics = self.monitor.get_metrics()
        metrics = {"cpu": metrics[2], "mem": metrics[3]}
        self.logger.info("metrics: {}".format(metrics))

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
            self.logger.info("Sleep affter scale: {}s".format(time_wait["up"]))
            time.sleep(time_wait["up"])
        elif(instances_delta['down'] > 0):
            self.scaler.scale(0-instances_delta['down'])
            self.logger.info("Sleep affter scale: {}s".format(time_wait["down"]))
            time.sleep(time_wait["down"])
