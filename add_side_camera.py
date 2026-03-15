import socket
import json

def add_side_camera():
    host = '127.0.0.1'
    port = 9876

    # Distance increased to 80m for fuller model coverage.
    # Elevation 20m, Target (0,0,5)
    # distance = 80, height_offset = 15 -> angle = atan(15/80) = 0.1853 rad
    # 90 deg + 0.1853 = 1.5708 + 0.1853 = 1.7561 rad

    try:
        with socket.create_connection((host, port), timeout=5) as s:
            code = """
import bpy
import math

# 1. Create the 'Side_Camera' if it doesn't exist
if "Side_Camera" not in bpy.data.objects:
    bpy.ops.object.camera_add(location=(0, -85, 20))
    side_cam = bpy.context.active_object
    side_cam.name = "Side_Camera"
    print("Created 'Side_Camera'")
else:
    side_cam = bpy.data.objects["Side_Camera"]
    side_cam.location = (0, -85, 20)
    print("Updated 'Side_Camera' location")

# 2. Set rotation to look at the center (approx Z=5)
# Using Track To constraint logic manually or precise Euler:
# Distance = 85, Height = 20 - 5 = 15. Angle = atan(15/85) = 0.1747 rad.
# Euler X = 90 deg + 0.1747 = 1.5708 + 0.1747 = 1.7455 rad.
side_cam.rotation_euler = (1.7455, 0, 0)

print(f"'Side_Camera' positioned at {side_cam.location} with rotation {side_cam.rotation_euler}")
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
    add_side_camera()
