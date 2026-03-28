import socket
import json

def create_final_flag():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import math

# 1. Cleanup existing flag objects
for obj in bpy.data.objects:
    if "Dutch_Flag" in obj.name or "Flagpost" in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)
for mesh in bpy.data.meshes:
    if "Dutch_Flag" in mesh.name or "Flagpost" in mesh.name:
        bpy.data.meshes.remove(mesh)

# 2. Flag Parameters
flag_width = 8.0
flag_height = 5.0
segments_x = 30
segments_z = 20

# Post parameters
post_x = -18.95
post_y = 0.0
post_z = 17.5
post_length = 8.0
post_dia = 0.2
tilt_deg = 15 # Backward tilt (towards -X)

# 3. Create Flagpost
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16, 
    radius=post_dia/2, 
    depth=post_length, 
    location=(0, 0, post_length/2)
)
post = bpy.context.active_object
post.name = "Flagpost"

# Select only the post to ensure context is correct for transform_apply
bpy.ops.object.select_all(action='DESELECT')
post.select_set(True)
bpy.context.view_layer.objects.active = post
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

tilt_rad = math.radians(-tilt_deg)
post.rotation_euler[1] = tilt_rad
post.location = (post_x, post_y, post_z)

# Material for Flagpost
if "Rib_Material" in bpy.data.materials:
    post.data.materials.append(bpy.data.materials["Rib_Material"])

# 4. Create Flag Mesh
mesh = bpy.data.meshes.new("Dutch_Flag_Mesh")
flag_obj = bpy.data.objects.new("Dutch_Flag", mesh)
bpy.context.collection.objects.link(flag_obj)

verts = []
faces = []

# Calculate post top position
top_offset_x = math.sin(tilt_rad) * post_length
top_offset_z = math.cos(tilt_rad) * post_length
top_pos = (post_x + top_offset_x, 0.0, post_z + top_offset_z)

# Correction for tilted hoist
tan_tilt = math.tan(tilt_rad)

for j in range(segments_z + 1):
    z_local = -j * (flag_height / segments_z)
    world_z = top_pos[2] + z_local
    
    # Calculate X position on the tilted pole for this height
    x_hoist_world = post_x + (world_z - post_z) * tan_tilt
    x_hoist_local = x_hoist_world - top_pos[0]
    
    for i in range(segments_x + 1):
        x_len_local = i * (flag_width / segments_x)
        x = x_hoist_local + x_len_local
        # Wave: sideways wave and amplitude as per last verified settings
        y = 0.3 * math.sin(i * 0.5 + 0.26) # 0.3 amplitude, mild wave
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

# 5. Materials
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
# Horizontal in world space, hoist correction handled in verts
flag_obj.rotation_euler = (0, 0, 0)

print("Created final Dutch flag (8x5m) with historical orientation and tilted hoist.")
"""

    payload = {
        "type": "execute_code",
        "params": {"code": code}
    }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(json.dumps(payload).encode('utf-8'))
            response = s.recv(1024 * 64)
            print(f"Blender response: {response.decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_final_flag()
