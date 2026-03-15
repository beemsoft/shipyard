import socket
import json

def get_scene_data():
    host = '127.0.0.1'
    port = 9876
    
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            code = """
import bpy
import json
data = {}
objs = ["Keel", "Sternpost", "Stempost", "Camera", "Camera_Back"]
for name in objs:
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        data[name] = {
            "location": list(obj.location),
            "dimensions": list(obj.dimensions),
            "rotation_euler": list(obj.rotation_euler)
        }
    else:
        data[name] = "Not found"
print(json.dumps(data))
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
                print(response)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_scene_data()
