__author__ = 'cuongnb14@gmail.com'

import logging

class Scaler(object):
    """docstring for ClassName"""
    def __init__(self, marathon_client, app):
        self.logger = logging.getLogger("Scaler")
        self.marathon_client = marathon_client
        self.app = app

    def scale(self, delta):
        """sacle app_name (add or remove) delta intances

        @param int delta number intances add if (delta > 0) or remove if (delta < 0)
        """
        current_instances = self.marathon_client.get_app("app-"+self.app.uuid).instances
        new_instance = current_instances + delta
        if(new_instance > self.app.max_instances):
            new_instance = self.app.max_instances
        if(new_instance < self.app.min_instances):
            new_instance = self.app.min_instances
        if(new_instance != current_instances):
            self.logger.info("scale to: %d", new_instance)
            self.marathon_client.scale_app("app-"+self.app.uuid, new_instance)
        else:
            self.logger.info("number instances to threshold, no scale!")
