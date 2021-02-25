# Simple Server Status

## Install

### Main Server

```bash
git clone https://github.com/panelssh/simple-server-status.git
cd simple-server-status
bash setup/main-setup.sh
ln -s /usr/local/dist/servers.json [DESTINATION_FOLDER]
```

### Client Server

```bash
curl -O https://raw.githubusercontent.com/panelssh/simple-server-status/main/setup/client-setup.sh
bash client-setup.sh [IP_MAIN_SERVER]
```

## Usage

### SysVinit

```bash
# start service
sudo systemctl start main-server.service
sudo systemctl start client-server.service

# restart service
sudo systemctl restart main-server.service
sudo systemctl restart client-server.service

# stop service
sudo systemctl stop main-server.service
sudo systemctl stop client-server.service

# status service
sudo systemctl status main-server.service
sudo systemctl status client-server.service

# enable service
sudo systemctl enable main-server.service
sudo systemctl enable client-server.service

# disable service
sudo systemctl disable main-server.service
sudo systemctl disable client-server.service

# remove service
sudo systemctl remove main-server.service
sudo systemctl remove client-server.service
```

### Systemd

```bash
# start service
sudo service main-server start
sudo service client-server start

# restart service
sudo service main-server restart
sudo service client-server restart

# stop service
sudo service main-server stop
sudo service client-server stop

# status service
sudo service main-server status
sudo service client-server status

# enable service
sudo update-rc.d main-server enable
sudo update-rc.d client-server enable

# disable service
sudo update-rc.d main-server disable
sudo update-rc.d client-server disable

# remove service
sudo update-rc.d main-server remove
sudo update-rc.d client-server remove
```
