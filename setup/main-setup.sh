#!/bin/bash

CWD=$(pwd)
CLIENT=""
KERNEL="sysvinit"
PY_SRC="${CWD}/main-server.py"
PY_DIST="/usr/local/share/main-server.py"

function initial_check() {
  if ! is_root; then
    echo "Sorry, you need to run this as root"
    exit 1
  fi

  if ! check_py; then
    echo "Python is not available"
    exit 1
  fi

  set_kernel
}

function is_root() {
  if [ "$EUID" -ne 0 ]; then
    return 1
  fi
}

function check_py() {
  if type python &>/dev/null; then
    CLIENT="python"
  elif type python3 &>/dev/null; then
    CLIENT="python3"
  fi

  if [ "$CLIENT" == "" ]; then
    return 1
  fi
}

function set_kernel() {
  if [ -f /proc/1/comm ]; then
    if grep -qi systemd /proc/1/comm; then
      KERNEL="systemd"
    fi
  fi

  if grep -qi systemd /proc/1/cmdline; then
    KERNEL="systemd"
  fi
}

function install() {
  local SERVER
  local SKIP
  local REPLACE
  local PORT
  local DATA
  local RUN_AS

  #SERVER=$(curl -s ifconfig.so)
  SERVER="localhost"

  if [ -f "$PY_SRC" ]; then
    SKIP=true
  fi

  if [ ! $SKIP ]; then
    PORT=35600
  else
    DATA=$(head -n 9 "$PY_SRC")
    PORT=$(echo "$DATA" | sed -n "s/SERVER_PORT\( \|\)=\( \|\)//p" | tr -d '"')
  fi

  if [ -f "${CWD}/src/main.py" ]; then
    sed -e "0,/^SERVER_HOST = .*$/s//SERVER_HOST = \"${SERVER}\"/" \
      -e "0,/^SERVER_PORT = .*$/s//SERVER_PORT = ${PORT}/" "${CWD}/src/main.py" >"$PY_SRC"
  else
    curl -Ls "https://git.io/main-server" | sed -e "0,/^SERVER_HOST = .*$/s//SERVER_HOST = \"${SERVER}\"/" \
      -e "0,/^SERVER_PORT = .*$/s//SERVER_PORT = ${PORT}/" "${CWD}/src/main.py" >"$PY_SRC"
  fi

  # shellcheck disable=SC2001
  PY_DIST=$(echo "$PY_SRC" | sed -e "s|${CWD}|/usr/local/share|g")
  cp -a "$PY_SRC" "$PY_DIST"

  mkdir -p /usr/local/dist
  cp "${CWD}/dist/servers.json" /usr/local/dist/servers.json

  # TODO: add interactive
  RUN_AS="root"

  if [ "$KERNEL" == "systemd" ]; then
    if ! id -u "$RUN_AS" >/dev/null 2>&1; then
      echo "The specified user \"$RUN_AS\" could not be found!"
      exit 1
    fi

    if [ -f /etc/systemd/system/main-server.service ]; then
      REPLACE=true
    fi

    if [ -f "${CWD}/setup/main-server.systemd" ]; then
      sed -e "s|^User=$|User=${RUN_AS}|" \
        -e "s|^ExecStart=$|ExecStart=${PY_DIST}|" "${CWD}/setup/main-server.systemd" > /etc/systemd/system/main-server.service
    else
      curl -Ls "https://git.io/main-server.systemd" | sed -e "s|^User=$|User=${RUN_AS}|" \
        -e "s|^ExecStart=$|ExecStart=${PY_DIST}|" > /etc/systemd/system/main-server.service
    fi

    chown "$RUN_AS" "$PY_DIST"
    chmod +x "$PY_DIST"
    chmod +x /etc/systemd/system/main-server.service

    if [ $REPLACE ]; then
      systemctl stop main-server.service
      sleep 1

      systemctl daemon-reload
    fi

    systemctl start main-server.service
    sleep 1

    systemctl status main-server.service
    sleep 1

    systemctl enable main-server.service

  elif [ "$KERNEL" == "sysvinit" ]; then
    if ! id -u "$RUN_AS" >/dev/null 2>&1; then
      echo "The specified user \"${RUN_AS}\" could not be found!"
      exit 1
    fi

    if [ -f /etc/init.d/main-server ]; then
      REPLACE=true
    fi

    if [ -f "${CWD}/setup/main-server.sysvinit" ]; then
      sed -e "s|^DAEMON=$|DAEMON=\"${PY_DIST}\"|" \
        -e "s|^RUN_AS=$|RUN_AS=\"${RUN_AS}\"|" "${CWD}/setup/main-server.sysvinit" > /etc/init.d/main-server
    else
      curl -Ls "https://git.io/main-server.sysvinit" | sed -e "s|^DAEMON=$|DAEMON=\"${PY_DIST}\"|" \
        -e "s|^RUN_AS=$|RUN_AS=\"${RUN_AS}\"|" > /etc/init.d/main-server
    fi

    chown "$RUN_AS" "$PY_DIST"
    chmod +x "$PY_DIST"
    chmod +x /etc/init.d/main-server

    if [ $REPLACE ]; then
      service main-server stop
      sleep 1
    fi

    service main-server start
    sleep 1

    service main-server status
    sleep 1

    update-rc.d main-server defaults
    sleep 1

    update-rc.d main-server enable
  fi
}

function uninstall() {
  read -p "Are you sure to uninstall? " -n 1 -r

  if [[ $REPLY =~ ^[^Yy]$ ]]; then
    exit 0
  fi

  echo ""

  if [ "$KERNEL" == "systemd" ]; then
    systemctl stop main-server.service
    sleep 1

    systemctl disable main-server.service
    sleep 1

    systemctl daemon-reload
    sleep 1

    rm -rf /etc/systemd/system/main-server.service
  elif [ "$KERNEL" == "sysvinit" ]; then
    service main-server stop
    sleep 1

    update-rc.d main-server disable
    sleep 1

    systemctl daemon-reload
    sleep 1

    rm -rf /etc/init.d/main-server
  fi

  rm -rf "$PY_SRC"
  rm -rf "$PY_DIST"
}

initial_check

if [[ -e "$PY_DIST" ]]; then
  uninstall
else
  install
fi
