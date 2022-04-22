#!/bin/bash
gnome-terminal --tab -e "python3 ./server/server_main.py"
gnome-terminal --tab -e "python3 ./client/client_main.py"
gnome-terminal --tab -e "python3 ./client/client_main.py"
