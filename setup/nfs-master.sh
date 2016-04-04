# install
sudo apt-get install nfs-kernel-server
sudo apt-get install portmap nfs-common
sudo apt-get install nfs-common

# declare file export
sudo echo "/autoscaling/storage/application *(rw,sync,no_subtree_check,no_root_squash)" >> /etc/exports

# restart
sudo /etc/init.d/nfs-kernel-server restart
sudo exportfs

# install plugin
wget https://github.com/gondor/docker-volume-netshare/releases/download/v0.13/docker-volume-netshare_0.13_amd64.deb
sudo dpkg -i docker-volume-netshare_0.13_amd64.deb

# run on startup
sudo sed -i "4iservice docker-volume-netshare start" /etc/rc.local
sudo sed -i "5isudo docker-volume-netshare nfs &" /etc/rc.local
