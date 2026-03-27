import socket
import json

def hide_sternpost():
    host = '127.0.0.1'
    port = 9876
    
    code = """
import bpy
if "Sternpost" in bpy.data.objects:
    bpy.data.objects["Sternpost"].hide_viewport = True
    bpy.data.objects["Sternpost"].hide_render = True
    print("Sternpost hidden successfully.")
else:
    print("Sternpost not found.")
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
                print(response)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    hide_sternpost()
