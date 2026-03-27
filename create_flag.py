import socket
import json

def create_flag():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import math

# 1. Cleanup existing flag and flagpost
for obj in bpy.data.objects:
    if "Flagpost" in obj.name or "Dutch_Flag" in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)
for mesh in bpy.data.meshes:
    if "Flagpost" in mesh.name or "Dutch_Flag" in mesh.name:
        bpy.data.meshes.remove(mesh)

# 2. Flagpost Parameters
# Taffrail arch top is at X=-19.0, Y=0, Z=17.5.
# Let's place the flagpost slightly tilted back from there.
post_x = -19.0
post_y = 0.0
post_z = 17.5
post_length = 8.0
post_dia = 0.2
tilt_deg = 15 # Tilt backwards

# Create Flagpost (Cylinder)
# We'll use a simple cylinder mesh
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16, 
    radius=post_dia/2, 
    depth=post_length, 
    location=(0, 0, 0)
)
post = bpy.context.active_object
post.name = "Flagpost"

# Rotation: Tilt backwards (around Y)
# The cylinder starts centered at (0,0,0) along Z.
# We want the base at (post_x, post_y, post_z).
# Move it up so base is at 0:
post.location = (0, 0, post_length/2)
bpy.ops.object.transform_apply(location=True)

# Apply tilt
post.rotation_euler[1] = math.radians(-tilt_deg)
post.location = (post_x, post_y, post_z)

# Material for Flagpost
if "Rib_Material" in bpy.data.materials:
    post.data.materials.append(bpy.data.materials["Rib_Material"])

# 3. Dutch Flag (Red, White, Blue)
flag_width = 6.0
flag_height = 4.0
segments_x = 10
segments_z = 10

# Create flag mesh
mesh = bpy.data.meshes.new("Dutch_Flag_Mesh")
flag_obj = bpy.data.objects.new("Dutch_Flag", mesh)
bpy.context.collection.objects.link(flag_obj)

verts = []
faces = []

# Generate a grid of vertices
for i in range(segments_x + 1):
    for j in range(segments_z + 1):
        x = i * (flag_width / segments_x)
        z = j * (flag_height / segments_z)
        # Add a slight wave (sine) for realism
        y = 0.2 * math.sin(i * 0.5) 
        verts.append((x, y, z))

for i in range(segments_x):
    for j in range(segments_z):
        v1 = i * (segments_z + 1) + j
        v2 = (i + 1) * (segments_z + 1) + j
        v3 = (i + 1) * (segments_z + 1) + (j + 1)
        v4 = i * (segments_z + 1) + (j + 1)
        faces.append((v1, v2, v3, v4))

mesh.from_pydata(verts, [], faces)
mesh.update()

# Materials for the flag
def create_flag_material(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs[0].default_value = color
    return mat

mat_red = create_flag_material("Flag_Red", (0.69, 0.0, 0.0, 1.0))
mat_white = create_flag_material("Flag_White", (1.0, 1.0, 1.0, 1.0))
mat_blue = create_flag_material("Flag_Blue", (0.0, 0.1, 0.4, 1.0))

flag_obj.data.materials.append(mat_red)
flag_obj.data.materials.append(mat_white)
flag_obj.data.materials.append(mat_blue)

# Assign materials to faces (3 horizontal stripes)
for poly in mesh.polygons:
    # poly.center.z ranges from 0 to flag_height
    z_rel = poly.center.z / flag_height
    if z_rel > 0.66:
        poly.material_index = 0 # Red
    elif z_rel > 0.33:
        poly.material_index = 1 # White
    else:
        poly.material_index = 2 # Blue

# Position flag on the post
# The flag should be attached to the top half of the post.
# Post top location:
top_offset_x = math.sin(math.radians(tilt_deg)) * post_length
top_offset_z = math.cos(math.radians(tilt_deg)) * post_length

# Attach flag near the top
flag_obj.location = (post_x + top_offset_x * 0.95, post_y, post_z + top_offset_z * 0.95 - flag_height)
# Tilt flag with post? Usually flags hang down but are attached.
# For simplicity, we keep it vertical but attached.
flag_obj.rotation_euler[1] = math.radians(-tilt_deg)

print("Created flagpost and big Dutch flag at the stern.")
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
    create_flag()
