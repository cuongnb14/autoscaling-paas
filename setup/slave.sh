HOST=192.168.122.53
ZK_HOST=192.168.122.51 

# config zookeper connection, for all hosts
echo zk://$ZK_HOST:2181/mesos > /etc/mesos/zk

# stop mesos master, zookeeper, marathon on slave
stop zookeeper
echo manual > /etc/init/zookeeper.override
stop mesos-master
echo manual > /etc/init/mesos-master.override
stop marathon
echo manual > /etc/init/marathon.override
stop chronos
echo manual > /etc/init/chronos.override

# Config slave
echo $HOST > /etc/mesos-slave/ip
cp /etc/mesos-slave/ip /etc/mesos-slave/hostname


# fix error mesos no start
rm -rf /tmp/mesos/

restart mesos-slave