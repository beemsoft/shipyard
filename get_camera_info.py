import socket
import json

def get_camera_info():
    host = '127.0.0.1'
    port = 9876
    
    code = """
import bpy
def cam_info(name):
    if name in bpy.data.objects:
        c = bpy.data.objects[name]
        return f"{name}: Lens={c.data.lens}mm, Clip={c.data.clip_start}-{c.data.clip_end}, Loc={list(c.location)}, Rot={list(c.rotation_euler)}"
    return f"{name}: NOT FOUND"

print(cam_info("Camera"))
print(cam_info("Camera_Back"))
print(cam_info("User_Perspective_Camera_Full"))
"""
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            command = {"type": "execute_code", "params": {"code": code}}
            s.sendall(json.dumps(command).encode('utf-8'))
            data = s.recv(16384)
            if data:
                print(json.loads(data.decode('utf-8'))["result"]["result"])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_camera_info()
