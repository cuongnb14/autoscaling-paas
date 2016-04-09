from apiv1.models import Setting
from marathon import MarathonClient, MarathonApp
import traceback
import json

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
    app_marathon = MarathonApp()
    for key, value in app_dict.items():
        setattr(app_marathon, key, value)
    return app_marathon

def get_message_serializer(status, message):
    data = {"status": status, "message": message}
    return MessageSerializer(data=data)

def get_db_app_marathon_name(database):
    return "{}.database.{}".format(database.user.username,database.id)

def get_user_dir(user):
    user_dir = "/autoscaling/storage/application/"+user.username
    return user_dir

def get_app_dir(app):
    app_dir = "/autoscaling/storage/application/"+app.uuid
    return app_dir

def get_database_dir(database):
    return "/autoscaling/storage/database/"+database.uuid
