import socket
import json

def update_side_camera():
    host = '127.0.0.1'
    port = 9876
    
    # Current: (0, -100, 40) with rotation (1.25, 0, 0)
    # Proposed: (0, -50, 15)
    # To look at (0, 0, 0.4) from (0, -50, 15):
    # Delta Z = 15 - 0.4 = 14.6
    # Delta Y = 50
    # Angle = atan(14.6/50) = 0.284 rad
    # Euler X rotation = 90 deg + 0.284 rad = 1.5708 + 0.284 = 1.8548 rad
    
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            code = """
import bpy
import math

if "Camera" in bpy.data.objects:
    cam = bpy.data.objects["Camera"]
    cam.location = (0, -50, 15)
    cam.rotation_euler = (1.8548, 0, 0)
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
