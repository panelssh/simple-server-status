#!/usr/bin/env python3

import os
import json
import socket
import time

SERVER_HOST = "localhost"
SERVER_PORT = 35600

# receive 4096 bytes each time
BUFFER_SIZE = 4096


def update_json_file(data):
    json_path = os.path.dirname(os.path.abspath(__file__)) + "/../dist/servers.json"

    # Open the JSON file for reading
    json_file = open(json_path, "r")
    servers = json.load(json_file)
    json_file.close()

    # Add or Update Data
    servers["servers"][data['hostname']] = data
    servers["updated_at"] = int(time.time())

    # Save our changes to JSON file
    json_file = open(json_path, "w+")
    json_file.write(json.dumps(servers))
    json_file.close()

    print("[*] JSON has been updated")


if __name__ == "__main__":
    socket.setdefaulttimeout(30)

    # create the server socket
    # TCP socket
    s = socket.socket()

    # bind the socket to our local address
    s.bind((SERVER_HOST, SERVER_PORT))

    # enabling our server to accept connections
    s.listen(0)
    print("[*] Listening as " + SERVER_HOST + ":" + str(SERVER_PORT))

    while 1:
        try:
            client_socket, address = s.accept()
            print("[*] Incoming request from: " + address[0])

            response = client_socket.recv(BUFFER_SIZE).decode()

            update_json_file(json.loads(response))

            client_socket.close()
        except KeyboardInterrupt:
            raise
        except socket.error as e:
            print("Socket Error:", e)
        except Exception as e:
            print("Caught Exception:", e)
