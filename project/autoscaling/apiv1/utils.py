from apiv1.models import Setting
from marathon import MarathonClient

def get_info_app(app, marathon_client):
    temp = {}
    temp['name'] = app.name
    temp['min_instances'] = app.min_instances
    temp['max_instances'] = app.max_instances
    try:
        marathon_app = marathon_client.get_app(app.name)
        temp['status'] = "Deployed"
        temp['port'] = marathon_app.container.docker.port_mappings[0].service_port
        temp['cpus'] = marathon_app.cpus
        temp['mem'] = marathon_app.mem
        temp['instances'] = marathon_app.instances
    except Exception as e:
        temp['status'] = "NotDeploy"
        temp['port'] = None
        temp['cpus'] = None
        temp['mem'] = None
        temp['instances'] = 0
    return temp

def get_marathon_client():
    try:
        MARATHON_HOST = "10.10.10.53"#Setting.objects.filter(name="marathon_host").first().value
        MARATHON_PORT = 8080#Setting.objects.get(name="marathon_port").first().value
        marathon_client = MarathonClient('http://{}:{}'.format(MARATHON_HOST, MARATHON_PORT))
        return marathon_client
    except Exception as e:
        raise Exception("unconnect to marathon")

def get_message_serializer(status, message):
    data = {"status": status, "message": message}
    return MessageSerializer(data=data)
