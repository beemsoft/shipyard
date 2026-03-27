import socket
import json
import math

def fix_flag_horizontal():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import math

# 1. Cleanup existing flag objects
for obj in bpy.data.objects:
    if "Dutch_Flag" in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)
for mesh in bpy.data.meshes:
    if "Dutch_Flag" in mesh.name:
        bpy.data.meshes.remove(mesh)

# 2. Flag Parameters
flag_width = 12.0
flag_height = 8.0
segments_x = 30
segments_z = 20

# Create flag mesh
mesh = bpy.data.meshes.new("Dutch_Flag_Mesh")
flag_obj = bpy.data.objects.new("Dutch_Flag", mesh)
bpy.context.collection.objects.link(flag_obj)

verts = []
faces = []

# Post parameters (from create_flag.py/animate_flag.py)
post_x = -19.0
post_z = 17.5
post_length = 8.0
tilt_deg = 15 # Backward tilt (towards -X)

# Calculate post top position
# The post is a cylinder from post_z to post_z + top_offset_z
# tilt_deg = 15 means top is at post_x + post_length * sin(-15)
tilt_rad = math.radians(-tilt_deg)
top_offset_x = math.sin(tilt_rad) * post_length
top_offset_z = math.cos(tilt_rad) * post_length
top_pos = (post_x + top_offset_x, 0.0, post_z + top_offset_z)

# The flag origin is at top_pos.
# To make it horizontal in world space while attached to the tilted pole:
# Local Z (up/down) will correspond to world Z.
# Local X (length) will correspond to world X.
# However, the hoist must be tilted.
# So at local Z = z_rel (where 0 is top, -flag_height is bottom),
# the hoist's world X is top_pos_x + (z_rel) * tan(-tilt).
# Then the flag length extends from there.

tan_tilt = math.tan(tilt_rad)

for j in range(segments_z + 1):
    z_local = -j * (flag_height / segments_z)
    # The hoist at this height is shifted by z_local * tan_tilt
    # Because for every unit down (-z), the pole shifts by -tan_tilt (since tilt_rad is negative, tan is negative)
    # Actually, if tilt is -15, as we go down (-z), we go towards the base which is at post_x.
    # top_x = post_x + top_offset_x
    # top_z = post_z + top_offset_z
    # x(z) = top_x + (top_z - z) * tan_tilt? No.
    # Let's use world Z directly.
    world_z = top_pos[2] + z_local
    # Pole X at world_z:
    # post_z is base_z. post_x is base_x.
    # (world_z - post_z) / post_length_z = (world_x - post_x) / post_length_x
    # No, simpler: world_x_on_pole = post_x + (world_z - post_z) * tan(-tilt_rad)? 
    # If tilt is -15 (backward), top is at -X relative to base.
    # base is at post_x, post_z. top is at post_x + sin(-15)*8, post_z + cos(-15)*8.
    # tan(-15) = sin(-15)/cos(-15).
    # so world_x = post_x + (world_z - post_z) * tan(tilt_rad)
    
    x_hoist_world = post_x + (world_z - post_z) * tan_tilt
    # X relative to top_pos[0]:
    x_hoist_local = x_hoist_world - top_pos[0]
    
    for i in range(segments_x + 1):
        x_len_local = i * (flag_width / segments_x)
        x = x_hoist_local + x_len_local
        y = 0.1 * math.sin(i * 0.5) # Slight wave for static realism
        z = z_local
        verts.append((x, y, z))

for i in range(segments_x):
    for j in range(segments_z):
        v1 = j * (segments_x + 1) + i
        v2 = j * (segments_x + 1) + (i + 1)
        v3 = (j + 1) * (segments_x + 1) + (i + 1)
        v4 = (j + 1) * (segments_x + 1) + i
        faces.append((v1, v2, v3, v4))

mesh.from_pydata(verts, [], faces)
mesh.update()

# Materials
def get_or_create_material(name, color):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs[0].default_value = color
    return mat

mat_red = get_or_create_material("Flag_Red", (0.69, 0.0, 0.0, 1.0))
mat_white = get_or_create_material("Flag_White", (1.0, 1.0, 1.0, 1.0))
mat_blue = get_or_create_material("Flag_Blue", (0.0, 0.1, 0.4, 1.0))

flag_obj.data.materials.append(mat_red)
flag_obj.data.materials.append(mat_white)
flag_obj.data.materials.append(mat_blue)

for poly in mesh.polygons:
    z_rel = -poly.center.z / flag_height
    if z_rel < 0.33:
        poly.material_index = 0
    elif z_rel < 0.66:
        poly.material_index = 1
    else:
        poly.material_index = 2

flag_obj.location = top_pos
# NO ROTATION - we want it horizontal in world space, and we handled the tilted hoist in vertex generation.
flag_obj.rotation_euler = (0, 0, 0)

# 6. No Animation (Wave modifier removed/not added)
# Just to be sure, remove Wave modifier if it exists (though we cleaned up the object)
for mod in flag_obj.modifiers:
    if mod.type == 'WAVE':
        flag_obj.modifiers.remove(mod)

print("Created horizontal Dutch flag pointing forward (backwind) with tilted hoist.")
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
    fix_flag_horizontal()
