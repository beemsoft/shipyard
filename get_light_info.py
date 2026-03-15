import socket
import json

def get_light_info():
    host = '127.0.0.1'
    port = 9876
    
    code = """
import bpy
results = {}
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        results[obj.name] = {
            "type": obj.data.type,
            "location": list(obj.location),
            "energy": obj.data.energy,
            "color": list(obj.data.color)
        }
print(results)
"""
    command = {
        "type": "execute_code",
        "params": {
            "code": code
        }
    }
    
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            s.sendall(json.dumps(command).encode('utf-8'))
            data = s.recv(16384)
            if data:
                response = json.loads(data.decode('utf-8'))
                print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_light_info()
