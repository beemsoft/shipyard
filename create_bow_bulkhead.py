import socket
import json

def create_bow_bulkhead():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import mathutils
import math

# 1. Clean up existing Bow_Bulkhead
for obj in bpy.data.objects:
    if obj.name.startswith("Bow_Bulkhead"):
        bpy.data.objects.remove(obj, do_unlink=True)
for mesh in bpy.data.meshes:
    if mesh.name.startswith("Bow_Bulkhead"):
        bpy.data.meshes.remove(mesh)

# 2. Parameters for the bulkhead
# Positioned near the front, where the stempost meets the deck level.
# Stempost ends at X = 18.95 + 7.5 = 26.45, Z = 15.4
# Let's place the bulkhead at X approx 22.0
x_bulkhead = 22.0
z_bulkhead_base = 8.0 # Starting from upper deck height roughly
width = 8.0 # Full width
height = 6.0 # Height of the bulkhead structure

# Create a plane and transform it to be a transverse bulkhead
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(x_bulkhead, 0, z_bulkhead_base + height/2))
bulkhead = bpy.context.active_object
bulkhead.name = "Bow_Bulkhead"

# Rotate to be transverse (perpendicular to X)
bulkhead.rotation_euler[1] = math.radians(90) # Rotate around Y
bulkhead.scale = (height, width, 1.0) # Z (height) -> now X, Y (width) -> now Y

# Apply scale
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# 3. Add a support hole or notch for the bowsprit
# The bowsprit typically passes through or over the bulkhead at an angle.
# For now, we'll just create a solid bulkhead as a base.

# 4. Material
if "Rib_Material" in bpy.data.materials:
    bulkhead.data.materials.append(bpy.data.materials["Rib_Material"])

print(f"Created Bow Bulkhead at X={x_bulkhead}")
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
    create_bow_bulkhead()
