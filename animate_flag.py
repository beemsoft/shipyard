import socket
import json

def animate_flag():
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

# 2. Dutch Flag Parameters (Horizontal and Blowing Forward)
flag_width = 12.0 # Made it larger for a 'big' flag effect
flag_height = 8.0
segments_x = 30 # High resolution for smooth waving
segments_z = 20

# Create flag mesh
mesh = bpy.data.meshes.new("Dutch_Flag_Mesh")
flag_obj = bpy.data.objects.new("Dutch_Flag", mesh)
bpy.context.collection.objects.link(flag_obj)

verts = []
faces = []

# Generate a grid of vertices
# To make it blow forward due to backwind:
# Wind is from stern (-X) towards bow (+X).
# Attachment is at the hoist (X=0).
# The flag extends along the X-axis (from 0 to flag_width).
# To make it relatively horizontal (blown by wind), we set Z to be slightly angled or use physics later.
# For now, let's keep it horizontal along X.
for i in range(segments_x + 1):
    for j in range(segments_z + 1):
        x = i * (flag_width / segments_x)
        z = -j * (flag_height / segments_z) # Hoist top at (0,0,0), hoist bottom at (0,0,-flag_height)
        y = 0.0
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

# 3. Materials for the flag (Red, White, Blue)
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

# Assign materials to faces (3 horizontal stripes)
for poly in mesh.polygons:
    z_rel = -poly.center.z / flag_height
    if z_rel < 0.33:
        poly.material_index = 0 # Red
    elif z_rel < 0.66:
        poly.material_index = 1 # White
    else:
        poly.material_index = 2 # Blue

# 4. Position and Attach the Flag
# Values from get_flag_locations.py for Flagpost and existing tilt
post_x = -19.0
post_z = 17.5
post_length = 8.0
tilt_deg = 15 # Tilt backwards

# Top of post (X, Z) calculation
top_offset_x = math.sin(math.radians(-tilt_deg)) * post_length
top_offset_z = math.cos(math.radians(-tilt_deg)) * post_length
top_pos = (post_x + top_offset_x, 0.0, post_z + top_offset_z)

flag_obj.location = top_pos
flag_obj.rotation_euler[1] = math.radians(-tilt_deg)

# 5. Add Wave Animation using Modifier
# This is better than manual vertex animation for a persistent effect
wave_mod = flag_obj.modifiers.new(name="FlagWave", type='WAVE')
wave_mod.use_x = True
wave_mod.use_y = True
wave_mod.height = 0.5
wave_mod.width = 3.0
wave_mod.narrowness = 2.0
wave_mod.speed = 0.2
wave_mod.falloff_radius = 0.0

# Pin the hoist (X=0) so it doesn't wave away from the post
# We need a vertex group for this
vg = flag_obj.vertex_groups.new(name="Pinned")
for v in mesh.vertices:
    # Pin vertices at the hoist (x near 0)
    if v.co.x < 0.1:
        # High weight at the very edge, then fall off?
        weight = 1.0
        vg.add([v.index], weight, 'REPLACE')
    elif v.co.x < 0.5:
        # Smooth transition for pinning
        weight = (0.5 - v.co.x) / 0.4
        vg.add([v.index], weight, 'REPLACE')

wave_mod.vertex_group = "Pinned"
# Actually Wave modifier pinning is inverted: 0 weight means fully affected, 1 means not affected?
# No, vertex_group controls the influence. 1 means affected.
# To pin it, we need 0 influence at the hoist.
# Let's flip the weights.
for v in mesh.vertices:
    weight = 1.0
    if v.co.x < 0.5:
        weight = v.co.x / 0.5
    vg.add([v.index], weight, 'REPLACE')

# 6. Set up Timeline for Animation
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250
bpy.context.scene.frame_current = 50 # Capture frame 50 for a mid-wave look in snapshots

print("Created waving Dutch flag pointing forward (backwind) with Wave modifier.")
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
    animate_flag()
