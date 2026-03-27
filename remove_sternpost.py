import socket
import json

def remove_sternpost():
    host = '127.0.0.1'
    port = 9876
    
    code = """
import bpy
# Cleanup existing sternpost
if "Sternpost" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Sternpost"], do_unlink=True)
for curve in bpy.data.curves:
    if curve.name.startswith("Sternpost"):
        bpy.data.curves.remove(curve)
print("Sternpost and associated curves removed.")
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
    remove_sternpost()
