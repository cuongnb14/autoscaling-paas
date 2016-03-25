from apiv1.models import Setting
from marathon import MarathonClient, MarathonApp
import traceback
import json

def get_info_app(app, marathon_client):
    temp = {}
    temp['name'] = app.name
    temp['github_url'] = app.github_url
    temp['min_instances'] = app.min_instances
    temp['max_instances'] = app.max_instances
    temp['env_hostname'] = app.env_hostname
    temp['env_port'] = app.env_port
    temp['env_db_hostname'] = app.env_db_hostname
    temp['env_db_port'] = app.env_db_port
    temp['env_db_name'] = app.env_db_name
    temp['env_db_username'] = app.env_db_username
    temp['env_db_password'] = app.env_db_password
    temp['status'] = app.status
    try:
        marathon_app = marathon_client.get_app("{}.{}".format(app.user.username,app.name))
        temp['port'] = marathon_app.container.docker.port_mappings[0].service_port
        temp['cpus'] = marathon_app.cpus
        temp['mem'] = marathon_app.mem
        temp['instances'] = marathon_app.instances
    except Exception as e:
        #traceback.print_exc()
        temp['port'] = None
        temp['cpus'] = None
        temp['mem'] = None
        temp['instances'] = 0
    return temp

def get_setting(key, default=None):
    setting = Setting.objects.filter(name=key).first()
    if setting:
        return setting.value
    return default

def get_marathon_client():
    try:
        MARATHON_HOST = get_setting("marathon_host", "10.10.10.51")
        MARATHON_PORT = int(get_setting("marathon_port", 8080))
        marathon_client = MarathonClient('http://{}:{}'.format(MARATHON_HOST, MARATHON_PORT))
        return marathon_client
    except Exception as e:
        raise Exception("unconnect to marathon")

def get_marathon_app(app_json):
    app_dict = json.loads(app_json)
    app_marathon = MarathonApp
    for key, value in app_dict.items():
        setattr(app_marathon, key, value)
    return app_marathon

def get_message_serializer(status, message):
    data = {"status": status, "message": message}
    return MessageSerializer(data=data)
