import socket
import json

def fix_flag_attachment():
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
post_x = -19.0
post_y = 0.0
post_z = 17.5
post_length = 8.0
post_dia = 0.2
tilt_deg = 15 # Tilt backwards (away from ship)

# Create Flagpost (Cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16, 
    radius=post_dia/2, 
    depth=post_length, 
    location=(0, 0, post_length/2)
)
post = bpy.context.active_object
post.name = "Flagpost"
bpy.ops.object.transform_apply(location=True)

# Apply tilt around Y
# Historical backward tilt: top moves towards -X
post.rotation_euler[1] = math.radians(tilt_deg)
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
# To attach the side of the flag to the top of the post, 
# let's make the origin (0,0,0) the top-left corner of the flag (hoist top).
# X will be from 0 to flag_width (into the wind)
# Z will be from 0 to -flag_height (hanging down)
for i in range(segments_x + 1):
    for j in range(segments_z + 1):
        x = i * (flag_width / segments_x)
        z = -j * (flag_height / segments_z)
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
    if name in bpy.data.materials:
        return bpy.data.materials[name]
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
# Since Z goes from 0 to -flag_height:
# -flag_height/3 to 0 is RED
# -2*flag_height/3 to -flag_height/3 is WHITE
# -flag_height to -2*flag_height/3 is BLUE
for poly in mesh.polygons:
    z_rel = -poly.center.z / flag_height
    if z_rel < 0.33:
        poly.material_index = 0 # Red
    elif z_rel < 0.66:
        poly.material_index = 1 # White
    else:
        poly.material_index = 2 # Blue

# Position flag on the post
# The flag's origin (0,0,0) is now its top-left corner.
# Post top location:
# If rotated by +tilt_deg around Y:
# X' = X*cos(y) + Z*sin(y) = 0*cos(y) + length*sin(y) = length*sin(y)
# Z' = -X*sin(y) + Z*cos(y) = -0*sin(y) + length*cos(y) = length*cos(y)
# In Blender, rotation around Y uses:
# X' = X*cos(y) + Z*sin(y)
# Z' = -X*sin(y) + Z*cos(y)
# So if y is positive (15 deg), X' is positive, top moves towards +X.
# If y is negative (-15 deg), X' is negative, top moves towards -X.
# So to move top towards -X, we need y = -15 degrees.
top_offset_x = math.sin(math.radians(-tilt_deg)) * post_length
top_offset_z = math.cos(math.radians(-tilt_deg)) * post_length

# Attach flag's top-left corner exactly at the top of the post
flag_obj.location = (post_x + top_offset_x, post_y, post_z + top_offset_z)

# The flag should rotate with the post but also hang down.
# Rotating by -tilt_deg around Y makes the hoist (X=0) parallel to the post.
flag_obj.rotation_euler[1] = math.radians(-tilt_deg)

print("Repositioned flag to be attached along the post from the top down.")
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
    fix_flag_attachment()
