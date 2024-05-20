import socket
import datetime
from datetime import datetime

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to a port
server_address = ('', 12345)
sock.bind(server_address)

print(f"Listening on port {12345}")

while True:
    # Listen for incoming broadcasts
    data, address = sock.recvfrom(4096)

    now = datetime.now()

    # Format the datetime object to show only up to the second
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # Print the received data and the sender's address
    print(f"{timestamp} Received {data} from {address}")
