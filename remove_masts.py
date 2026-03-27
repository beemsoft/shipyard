import socket
import json

def remove_masts():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy

# Clean up all mast-related objects
import bpy
masts_to_remove = [obj for obj in bpy.data.objects if any(name.lower() in obj.name.lower() for name in ["Mast", "Top_", "Bowsprit", "Yard", "Crossjack"])]
for obj in masts_to_remove:
    bpy.data.objects.remove(obj, do_unlink=True)

# Also clean up related meshes
for mesh in list(bpy.data.meshes):
    if any(name.lower() in mesh.name.lower() for name in ["Mast", "Top_", "Bowsprit", "Yard", "Crossjack"]):
        bpy.data.meshes.remove(mesh)

# Clean up related curves (if any)
for curve in list(bpy.data.curves):
    if any(name.lower() in curve.name.lower() for name in ["Mast", "Top_", "Bowsprit", "Yard", "Crossjack"]):
        bpy.data.curves.remove(curve)

print(f"Removed {len(masts_to_remove)} mast-related objects.")
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
    remove_masts()
