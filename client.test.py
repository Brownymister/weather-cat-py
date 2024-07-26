import bluetooth

# Scan for devices
print("Scanning...")
devices = bluetooth.discover_devices(lookup_names=True)

for addr, name in devices:
    print(f"Found {name} ({addr})")

# Attempt to connect to the first found device
target_name = "mpy-uart"
target_address = None

for device_addr, device_name in devices:
    if target_name == device_name:
        target_address = device_addr
        break

if target_address is not None:
    print(f"Connecting to {target_name} at address {target_address}")
    port = 1  # RFCOMM channel
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((target_address, port))
    print("Connected!")
else:
    print("Could not find target Bluetooth device named \"{}\"".format(target_name))

sock.close()

