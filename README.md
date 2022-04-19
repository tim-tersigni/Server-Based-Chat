# Server-Based-Chat
A group project for computer networking.
Instructions: https://github.com/tim-tersigni/Server-Based-Chat/files/8460323/ServerBasedChat.pdf

## Setup
- Uses python 3.8 and above. Built using 3.8.10.
- Requirements.txt contains a list of used modules which must be installed.
- Run $```pip install -r requirements.txt``` to automatically install required modules

## Example Subscriber Data
- To generate a list of example subscribers, run populate_subscribers.py: ```python3 ./server/populate_subscribers.py```

## Running Server and Clients
- Run server_main.py to launch server: ```python3 ./server/server_main.py```
- Run client_main.py to launch a client instance: ```python3 ./client/client_main.py```
- To run client as an authenticated subscriber, make sure to enter a client id listed in ./server/subscribers.data
