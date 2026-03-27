import socket
import json
import math

def fix_back_camera():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import math

# Bounding Box: {"min": [-20.6, -7.1, -0.2], "max": [33.4, 7.1, 44.0]}
# Center: X=6.4, Y=0, Z=21.9
# Height: 44.2m

# Back Camera current position: X=-110.0, Y=0.0, Z=22.0
# The user says the bottom is missing.
# Let's move the camera a bit lower and tilt it slightly up or move it further back.
# Moving the camera lower to Z=15.0 and aiming for the ship's center (21.9) could help, 
# or just move it further back to capture everything.
# Let's move it to X=-130.0 and lower it to Z=21.0 to ensure the keel is visible.

cam_name = "Camera_Back"
if cam_name in bpy.data.objects:
    cam = bpy.data.objects[cam_name]
    cam.location = (-130.0, 0.0, 21.0)
    # Keeping rotation same for now (vertical, facing +X)
    print(f"Updated {cam_name} to X=-130.0, Z=21.0")
else:
    print(f"Camera '{cam_name}' not found")
"""

    try:
        with socket.create_connection((host, port), timeout=30) as s:
            command = {
                "type": "execute_code",
                "params": {
                    "code": code
                }
            }
            s.sendall(json.dumps(command).encode('utf-8'))
            data = s.recv(16384)
            if data:
                response = json.loads(data.decode('utf-8'))
                print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_back_camera()
