#install nfs
sudo apt-get -y install nfs-common

# install plugin
wget https://dl.bintray.com//content/pacesys/docker/docker-volume-netshare_0.12_i386.deb
sudo dpkg -i docker-volume-netshare_0.12_i386.deb

# run on startup
sudo sed -i "4iservice docker-volume-netshare start" /etc/rc.local
sudo sed -i "5isudo docker-volume-netshare nfs &" /etc/rc.local
