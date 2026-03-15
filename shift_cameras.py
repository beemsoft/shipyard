import socket
import json

def shift_cameras_back():
    host = '127.0.0.1'
    port = 9876

    # Current positions:
    # Camera (Side): (0, -50, 15)
    # Camera_Back: (-40, 0, 15)

    # We will shift them back:
    # Camera (Side) -> (0, -75, 20)  - Further back and slightly higher for better perspective
    # Camera_Back -> (-60, 0, 20)    - Further back and slightly higher

    code = """
import bpy

def update_camera_pos(name, loc):
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        obj.location = loc
        print(f"Updated '{name}' position to {loc}")
    else:
        print(f"Camera '{name}' not found")

update_camera_pos("Camera", (0, -75, 20))
update_camera_pos("Camera_Back", (-60, 0, 20))
"""
    command = {
        "type": "execute_code",
        "params": {
            "code": code
        }
    }

    try:
        with socket.create_connection((host, port), timeout=30) as s:
            s.sendall(json.dumps(command).encode('utf-8'))
            data = s.recv(16384)
            if data:
                response = json.loads(data.decode('utf-8'))
                print("Blender response:")
                print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    shift_cameras_back()
