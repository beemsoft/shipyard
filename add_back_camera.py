import socket
import json

def add_back_camera():
    host = '127.0.0.1'
    port = 9876
    
    # Keel length is 37.9m (along the X-axis, centered at 0,0,0)
    # The back of the ship (stern) is at X = -18.95.
    # We'll position the camera at X = -100 to look towards the center (0,0,5) from the back.
    # distance = 100, height = 25 -> elevation offset = 20 (Target Z=5)
    # Angle: atan(20/100) = 0.1974 rad
    # Euler rotation (in radians):
    # To look towards +X, we need Z rotation = 90 deg (pi/2) = 1.5708
    # To look slightly down, we need X rotation = 90 deg + 0.1974 = 1.7682 rad
    
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            code = """
import bpy
import math

# 1. Create the 'Camera_Back' if it doesn't exist
if "Camera_Back" not in bpy.data.objects:
    bpy.ops.object.camera_add(location=(-100, 0, 25))
    cam_back = bpy.context.active_object
    cam_back.name = "Camera_Back"
    print("Created 'Camera_Back'")
else:
    cam_back = bpy.data.objects["Camera_Back"]
    cam_back.location = (-100, 0, 25)
    print("Updated 'Camera_Back' location")

# 2. Set rotation to look at the center from the back (stern view)
cam_back.rotation_euler = (1.7682, 0, 1.5708)

print(f"'Camera_Back' positioned at {cam_back.location} with rotation {cam_back.rotation_euler}")
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
    add_back_camera()
