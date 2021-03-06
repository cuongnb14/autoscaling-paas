__author__ = "cuongnb14@gmail.com"

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey

Base = declarative_base()

class WebApp(Base):
    """Mapping with table apps"""
    __tablename__ = 'autoscaling_web_app'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    uuid = Column(String, unique=True)
    min_instances = Column(Integer)
    max_instances = Column(Integer)
    cpus = Column(Float)
    mem = Column(Float)
    policies = relationship("Policy", order_by="Policy.id", backref="app", cascade="all, delete, delete-orphan")

class Policy(Base):
    """Mapping with table policies"""
    __tablename__ = 'autoscaling_policies'

    id = Column(Integer, primary_key=True)
    web_app_id = Column(String, ForeignKey('autoscaling_web_app.id'))
    metric_type = Column(String)
    upper_threshold = Column(Float)
    lower_threshold = Column(Float)
    instances_out = Column(Integer)
    instances_in = Column(Integer)
    scale_up_wait = Column(Integer)
    scale_down_wait = Column(Integer)
