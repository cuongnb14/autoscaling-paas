__author__ = "cuongnb14@gmail.com"

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey

Base = declarative_base()

class App(Base):
    """Mapping with table apps"""
    __tablename__ = 'apps'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    min_instances = Column(Integer)
    max_instances = Column(Integer)
    policies = relationship("Policy", order_by="Policy.id", backref="app", cascade="all, delete, delete-orphan")

class Policy(Base):
    """Mapping with table policies"""
    __tablename__ = 'policies'

    id = Column(Integer, primary_key=True)
    app_id = Column(String, ForeignKey('apps.id'))
    metric_type = Column(String)
    upper_threshold = Column(Float)
    lower_threshold = Column(Float)
    instances_out = Column(Integer)
    instances_in = Column(Integer)
    scale_up_wait = Column(Integer)
    scale_down_wait = Column(Integer)


