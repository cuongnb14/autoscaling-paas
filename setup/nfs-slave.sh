#install nfs
sudo apt-get -y install nfs-common

# install plugin
wget https://github.com/gondor/docker-volume-netshare/releases/download/v0.13/docker-volume-netshare_0.13_amd64.deb
sudo dpkg -i docker-volume-netshare_0.13_amd64.deb

# run on startup
sudo sed -i "4iservice docker-volume-netshare start" /etc/rc.local
sudo sed -i "5isudo docker-volume-netshare nfs &" /etc/rc.local
:
