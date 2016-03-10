from django.db import models
from core.models import TimeStampedModel
from django.contrib.auth.models import User

# Create your models here.
class WebApp(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    apache_version = models.CharField(max_length=10)
    min_instances = models.IntegerField()
    max_instances = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "autoscaling_web_app"

class DatabaseApp(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    host = models.CharField(max_length=45)
    port = models.IntegerField()
    root_password = models.CharField(max_length=60)
    mysql_version = models.CharField(max_length=10)
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
        db_table = "policies"

        