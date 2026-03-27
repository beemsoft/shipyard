import socket
import json

def create_stern_transoms():
    host = '127.0.0.1'
    port = 9876

    # Historical data:
    # Sternpost top is at X = -18.95, Z = 10.0 (from report 2026-03-15)
    # Keel is at Z=0.4.
    # We'll place 4 transoms between Z=4 and Z=10.

    code = """
import bpy
import math

def create_material(name, color):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.diffuse_color = color
    return mat

# Cleanup existing transoms
for obj in bpy.data.objects:
    if "Transom" in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)

# Transom Data (Height Z, Width Y, Depth X-scale)
# The Wing Transom (top) is the widest.
transoms = [
    {"name": "Wing_Transom", "z": 9.5, "width": 8.0, "thickness": 0.6},
    {"name": "Transom_2", "z": 8.0, "width": 7.2, "thickness": 0.5},
    {"name": "Transom_3", "z": 6.5, "width": 6.0, "thickness": 0.5},
    {"name": "Lower_Transom", "z": 5.0, "width": 4.5, "thickness": 0.5}
]

mat = create_material("Wood_Material", (0.1, 0.05, 0.02, 1.0))
ship_x_pos = -18.95 # Position of sternpost

for t in transoms:
    # Create a cube for each transom
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ship_x_pos, 0, t["z"]))
    obj = bpy.context.active_object
    obj.name = t["name"]
    # Scale: X (depth), Y (width), Z (height)
    obj.scale = (t["thickness"], t["width"], 0.4)
    obj.data.materials.append(mat)
    
print(f"Created {len(transoms)} transoms at the sternpost.")
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
    create_stern_transoms()
