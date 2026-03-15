import socket
import json

def list_cameras():
    host = '127.0.0.1'
    port = 9876
    
    code = """
import bpy
print("CAMERAS:")
for obj in bpy.data.objects:
    if obj.type == 'CAMERA':
        print(f"CAMERA: {obj.name} Location: {list(obj.location)} Rotation: {list(obj.rotation_euler)}")
"""
    try:
        with socket.create_connection((host, port), timeout=5) as s:
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
    list_cameras()
