import socket
import json
import math

def fix_flag_sideways():
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
flag_width = 8.0
flag_height = 5.0
segments_x = 30
segments_z = 20
sideway_angle_deg = 15 # Wave sideways by 15 degrees

# Create flag mesh
mesh = bpy.data.meshes.new("Dutch_Flag_Mesh")
flag_obj = bpy.data.objects.new("Dutch_Flag", mesh)
bpy.context.collection.objects.link(flag_obj)

verts = []
faces = []

# Post parameters (from previous versions)
post_x = -19.0
post_z = 17.5
post_length = 8.0
tilt_deg = 15 # Backward tilt (towards -X)

tilt_rad = math.radians(-tilt_deg)
top_offset_x = math.sin(tilt_rad) * post_length
top_offset_z = math.cos(tilt_rad) * post_length
top_pos = (post_x + top_offset_x, 0.0, post_z + top_offset_z)

tan_tilt = math.tan(tilt_rad)
sideway_rad = math.radians(sideway_angle_deg)

for j in range(segments_z + 1):
    z_local = -j * (flag_height / segments_z)
    world_z = top_pos[2] + z_local
    x_hoist_local = z_local * tan_tilt
    
    for i in range(segments_x + 1):
        x_len_local = i * (flag_width / segments_x)
        
        # Apply sideway rotation (around Z at the hoist)
        # In local space relative to top_pos, x_hoist_local is the pivot for this z-level.
        # Original: x = x_hoist_local + x_len_local, y = 0
        # New: Rotate x_len_local around Y-axis (vertical in local) at x_hoist_local
        
        x = x_hoist_local + x_len_local * math.cos(sideway_rad)
        y = x_len_local * math.sin(sideway_rad)
        
        # Add a more pronounced sine wave for realism
        y += 0.3 * math.sin(i * 0.4) 
        
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
flag_obj.rotation_euler = (0, 0, 0)

print(f"Created sideways waving Dutch flag (8m x 5m, angle: {sideway_angle_deg}deg) pointing forward.")
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
    fix_flag_sideways()
