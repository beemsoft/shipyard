import socket
import json

def delete_user_camera():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy

def delete_object(name):
    obj = bpy.data.objects.get(name)
    if obj:
        # If it's a camera, also delete its data
        if obj.type == 'CAMERA':
            cam_data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.cameras.remove(cam_data, do_unlink=True)
            print(f"Deleted camera object and data: {name}")
        else:
            bpy.data.objects.remove(obj, do_unlink=True)
            print(f"Deleted object: {name}")
    else:
        print(f"Object not found: {name}")

delete_object("User_Perspective_Camera_Full")
delete_object("Target_User_Perspective_Camera_Full")
"""

    payload = {
        "type": "execute_code",
        "params": {"code": code}
    }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(json.dumps(payload).encode('utf-8'))
            response = s.recv(1024 * 64)
            print(f"Blender response: {response.decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    delete_user_camera()
