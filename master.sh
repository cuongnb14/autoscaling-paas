# Setup node master have run slave
HOST=192.168.122.51

# config zookeper connection, for all hosts
echo zk://$HOST:2181/mesos > /etc/mesos/zk

# config zookeper on master node
echo 1 > /etc/zookeeper/conf/myid # id for master server
echo server.1=$HOST:2888:3888 >> /etc/zookeeper/conf/zoo.cfg # zookeper mapping master server

# config mesos
echo 1 > /etc/mesos-master/quorum
echo $HOST > /etc/mesos-master/ip
cp /etc/mesos-master/ip /etc/mesos-master/hostname

# config marathon
mkdir -p /etc/marathon/conf
cp /etc/mesos-master/hostname /etc/marathon/conf
cp /etc/mesos/zk /etc/marathon/conf/master
cp /etc/marathon/conf/master /etc/marathon/conf/zk
echo zk://$HOST:2181/marathon > /etc/marathon/conf/zk

# Configure Service Init Rules and Restart Services
restart zookeeper
start mesos-master
start marathon

# Config slave
echo $HOST > /etc/mesos-slave/ip
cp /etc/mesos-slave/ip /etc/mesos-slave/hostname
# fix error mesos no start
rm -rf /tmp/mesos/

restart mesos-slave

# Haproxy
add-apt-repository ppa:vbernat/haproxy-1.6
apt-get update
apt-get install haproxy
