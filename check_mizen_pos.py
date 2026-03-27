import socket
import json

def get_ship_info():
    host = '127.0.0.1'
    port = 9876
    code = """
import bpy
import json
data = {}
for obj in bpy.data.objects:
    if any(k in obj.name for k in ["Mizen", "Dutch_Flag", "Flagpost"]):
        data[obj.name] = list(obj.location)
print(json.dumps(data))
"""
    try:
        with socket.create_connection((host, port), timeout=10) as s:
            s.sendall(json.dumps({"type": "execute_code", "params": {"code": code}}).encode('utf-8'))
            resp = s.recv(16384).decode('utf-8')
            print(resp)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_ship_info()
