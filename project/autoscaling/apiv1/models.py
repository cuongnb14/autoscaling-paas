from django.db import models
from core.models import TimeStampedModel
from django.contrib.auth.models import User

# Create your models here.
class WebApp(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    github_url = models.CharField(max_length=255)
    min_instances = models.IntegerField()
    max_instances = models.IntegerField()
    status = models.CharField(max_length=30, default="cloning")
    autoscaling = models.CharField(max_length=255, default='off')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "autoscaling_web_app"

class DatabaseImage(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    type_db = models.CharField(max_length=10)
    version = models.CharField(max_length=10)
    image_name = models.CharField(max_length=45)

    class Meta:
        db_table = "autoscaling_database_image"

class DatabaseApp(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    host = models.CharField(max_length=45)
    port = models.IntegerField()
    username = models.CharField(max_length=45)
    root_password = models.CharField(max_length=60)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(DatabaseImage, on_delete=models.CASCADE)

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
