### Author: Nguyen Phan

### Contact: nguyenpkk95@gmail.com

### Desc:
An implementation of the reverse proxy load balancer (RPLB), a client that can send and receive a json message, a server that can register with the RPLB and receive/reply with the json message.

### NOTES:
- **The ClientID passed into the Client's start parameter will OVERRIDE the srcid in the packet to be sent!**
- Both the server and the RPLB can receive multiple messages at the same time, which means that not only can multiple clients connect to the RPLB at the same time, but the server can also receive multiple messages.