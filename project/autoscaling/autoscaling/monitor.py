__author__ = 'cuongnb14@gmail.com'


class Monitor(object):
    """docstring for Moniter"""

    def __init__(self, influxdb_client, app):
        """init

        @param model.WebApp app
        """
        self.influxdb_client = influxdb_client
        self.app = app

    def get_metrics(self):
        query = "SELECT COUNT(DISTINCT(mesos_task_id)), MEAN(cpu_usage), MEAN(mem_usage)  FROM monitoring where app_uuid = 'app-{}' and time > now()-1m group by time(10s)".format(self.app.uuid)
        metrics = self.influxdb_client.query(query)
        if metrics:
            points = metrics[0]["points"]
            if points:
                return points[0]
        return None
