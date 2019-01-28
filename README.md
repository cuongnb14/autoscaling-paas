# autoscaling-paas
autoscaling on mesos 

## 1. Install infrastructure

Install mesos on 3 node:
- Node 1: Zookeeper, mesos-master, meosos-slave and marathon
- Node 2: mesos-slave
- Node 3: mesos-slave
and install docker on all node

### 1.1 Install docker

On all node:
```
sudo wget -qO- https://get.docker.com/ | sh
sudo usermod -aG docker `whoami`
```
### 1.2 Install mesos

- On node 1: install java8 for marathon 
```
sudo add-apt-repository ppa:webupd8team/java -y
sudo apt-get update
sudo apt-get install oracle-java8-installer
sudo apt-get install oracle-java8-set-default
```

- On all node:
```
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv E56151BF
DISTRO=$(lsb_release -is | tr '[:upper:]' '[:lower:]')
CODENAME=$(lsb_release -cs)
echo "deb http://repos.mesosphere.io/${DISTRO} ${CODENAME} main" | sudo tee /etc/apt/sources.list.d/mesosphere.list
sudo apt-get -y update
sudo apt-get install mesosphere
```
- Config mesos: use 2 file script `master.sh` and `slave.sh` (note: change ip for each node in scripts)
  - On node 1: Run script `master.sh`
  - On node 2,3: Run script `slave.sh`

