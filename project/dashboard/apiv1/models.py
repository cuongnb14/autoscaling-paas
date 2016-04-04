from django.db import models
from core.models import TimeStampedModel
from django.contrib.auth.models import User

# Create your models here.
class WebApp(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=60)
    name = models.CharField(max_length=30, unique=True)
    github_url = models.CharField(max_length=255)
    min_instances = models.IntegerField()
    max_instances = models.IntegerField()
    cpus = models.FloatField(default=0.5)
    mem = models.FloatField(default=64)
    status = models.CharField(max_length=30, default="cloning")
    autoscaling = models.BooleanField(default="0")
    env_hostname = models.CharField(max_length=45, default='10.10.10.51')
    env_port = models.IntegerField(default=0)
    env_db_hostname =  models.CharField(max_length=45, default='10.10.10.51')
    env_db_port =  models.IntegerField(default=0)
    env_db_username =  models.CharField(max_length=45, default='')
    env_db_password = models.CharField(max_length=45, default='')
    env_db_name = models.CharField(max_length=45, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "autoscaling_web_app"

class DatabaseApp(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=60)
    host = models.CharField(max_length=45)
    port = models.IntegerField(default=0)
    root_password = models.CharField(max_length=60)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "autoscaling_database_app"



class Policy(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    web_app = models.ForeignKey(WebApp, on_delete=models.CASCADE)
    metric_type = models.CharField(max_length=30)
    upper_threshold = models.FloatField()
    lower_threshold = models.FloatField()
    instances_out = models.IntegerField()
    instances_in = models.IntegerField()
    scale_up_wait = models.IntegerField()
    scale_down_wait = models.IntegerField()
    disabled = models.BooleanField(default=False)

    class Meta:
        db_table = "autoscaling_policies"

class Setting(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    value = models.TextField()

    class Meta:
        db_table = "autoscaling_setting"
