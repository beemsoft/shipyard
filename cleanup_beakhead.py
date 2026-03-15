import socket
import json

def cleanup_beakhead():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy

# Cleanup Beakhead related objects
prefixes = ["Beakhead", "Bowsprit_Support", "R_Path", "L_Path", "Knee_Profile", "Beak_Profile"]
for obj in bpy.data.objects:
    for prefix in prefixes:
        if obj.name.startswith(prefix):
            bpy.data.objects.remove(obj, do_unlink=True)
            break

for mesh in bpy.data.meshes:
    for prefix in prefixes:
        if mesh.name.startswith(prefix):
            bpy.data.meshes.remove(mesh)
            break

for curve in bpy.data.curves:
    for prefix in prefixes:
        if curve.name.startswith(prefix):
            bpy.data.curves.remove(curve)
            break

print("Cleaned up beakhead related objects.")
"""

    try:
        with socket.create_connection((host, port), timeout=30) as s:
            command = {
                "type": "execute_code",
                "params": {
                    "code": code
                }
            }
            s.sendall(json.dumps(command).encode('utf-8'))
            data = s.recv(16384)
            if data:
                print(json.dumps(json.loads(data.decode('utf-8')), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    cleanup_beakhead()
