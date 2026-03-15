import socket
import json

def remove_side_camera():
    host = '127.0.0.1'
    port = 9876
    
    code = """
import bpy
if "Side_Camera" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Side_Camera"], do_unlink=True)
    print("Side_Camera removed")
else:
    print("Side_Camera not found")
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
                print(json.loads(data.decode('utf-8')))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    remove_side_camera()
