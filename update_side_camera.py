import socket
import json

def update_side_camera():
    host = '127.0.0.1'
    port = 9876

    # Distance increased to 100m for better coverage
    # Elevation 25m, Target (0,0,5) -> Height_offset = 20
    # Angle = atan(20/100) = 0.1974 rad
    # Euler X rotation = 90 deg + 0.1974 rad = 1.5708 + 0.1974 = 1.7682 rad

    try:
        with socket.create_connection((host, port), timeout=5) as s:
            code = """
import bpy
import math

if "Camera" in bpy.data.objects:
    cam = bpy.data.objects["Camera"]
    cam.location = (0, -100, 25)
    # Distance = 100, Height_offset = 20 (Target Z=5). Angle = atan(20/100) = 0.1974 rad.
    # Euler X = 90 deg + 0.1974 = 1.5708 + 0.1974 = 1.7682 rad.
    # Looking from -Y towards +Y means Z rotation = 0 deg
    cam.rotation_euler = (1.7682, 0, 0)
    print(f"Updated 'Camera' (side) to {cam.location} with rotation {cam.rotation_euler}")
else:
    print("'Camera' not found")
"""
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
                print("Blender response:")
                print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_side_camera()
