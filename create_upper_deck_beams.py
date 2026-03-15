import socket
import json

def create_upper_deck_beams_and_knees():
    host = '127.0.0.1'
    port = 9876

    # Real-size dimensions
    keel_length = 37.9
    half_length = keel_length / 2.0
    num_ribs = 15
    start_x = -17.5
    end_x = 17.5
    rib_range = end_x - start_x
    spacing = rib_range / (num_ribs - 1)

    # Python code for Blender
    code = f"""
import bpy
import mathutils
import math

def create_beam(name, x, width, z, thickness, material_name):
    # A simple rectangular beam across the ship
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Vertices for a box: width x thickness x thickness
    # Centered at (x, 0, z)
    hw = width
    ht = thickness / 2.0
    
    verts = [
        (x, -hw, z - ht), (x, hw, z - ht), (x, hw, z + ht), (x, -hw, z + ht),
        (x + thickness, -hw, z - ht), (x + thickness, hw, z - ht), (x + thickness, hw, z + ht), (x + thickness, -hw, z + ht)
    ]
    faces = [
        (0,1,2,3), (4,5,6,7), (0,4,7,3), (1,5,6,2), (0,1,5,4), (3,2,6,7)
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    if material_name in bpy.data.materials:
        obj.data.materials.append(bpy.data.materials[material_name])
    return obj

def create_knee(name, x, y, z, size, thickness, orientation, material_name):
    # Create an L-shaped "knee" at (x, y, z)
    # orientation: 'LEFT' or 'RIGHT'
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    s = size
    t = thickness
    # L shape: one arm along beam (Y), one arm down along rib (Z)
    if orientation == 'RIGHT':
        # Points in Y-Z plane
        verts = [
            (x, y, z), (x, y - s, z), (x, y - s, z - t), (x, y - t, z - t), (x, y - t, z - s), (x, y, z - s),
            (x + t, y, z), (x + t, y - s, z), (x + t, y - s, z - t), (x + t, y - t, z - t), (x + t, y - t, z - s), (x + t, y, z - s)
        ]
    else: # LEFT
        verts = [
            (x, y, z), (x, y + s, z), (x, y + s, z - t), (x, y + t, z - t), (x, y + t, z - s), (x, y, z - s),
            (x + t, y, z), (x + t, y + s, z), (x + t, y + s, z - t), (x + t, y + t, z - t), (x + t, y + t, z - s), (x + t, y, z - s)
        ]
    
    faces = [
        (0,1,2,3,4,5), (6,7,8,9,10,11), # Front/Back
        (0,6,7,1), (1,7,8,2), (2,8,9,3), (3,9,10,4), (4,10,11,5), (5,11,6,0) # Sides
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    if material_name in bpy.data.materials:
        obj.data.materials.append(bpy.data.materials[material_name])
    return obj

# Clean up
for obj in bpy.data.objects:
    if obj.name.startswith("Upper_Beam") or obj.name.startswith("Upper_Knee_"):
        bpy.data.objects.remove(obj, do_unlink=True)

# Material
if "Rib_Material" not in bpy.data.materials:
    mat = bpy.data.materials.new(name="Rib_Material")
    mat.diffuse_color = (0.2, 0.1, 0.05, 1.0)
else:
    mat = bpy.data.materials["Rib_Material"]

num_ribs = {num_ribs}
start_x = {start_x}
spacing = {spacing}
half_length = {half_length}

for i in range(num_ribs):
    x = start_x + (i * spacing)
    
    # Calculate height and width at deck level (approx 3m above lower deck)
    # Find keel top Z
    keel_top_z = 0.0
    if "Keel" in bpy.data.objects:
        keel = bpy.data.objects["Keel"]
        ray_origin = mathutils.Vector((x, 0.0, 10.0))
        ray_direction = mathutils.Vector((0.0, 0.0, -1.0))
        inv_world = keel.matrix_world.inverted()
        origin_local = inv_world @ ray_origin
        direction_local = inv_world.to_quaternion() @ ray_direction
        hit, loc, norm, index = keel.ray_cast(origin_local, direction_local)
        if hit:
            world_loc = keel.matrix_world @ loc
            keel_top_z = world_loc.z

    # Lower deck was at +3.5. Upper deck approx 2.5m higher.
    deck_height = keel_top_z + 6.0
    
    # 0. Find the exact width by ray-casting against the corresponding Rib object
    beam_width = 2.5 # Default fallback
    rib_name = f"Rib_{{i:02d}}"
    if rib_name in bpy.data.objects:
        rib_obj = bpy.data.objects[rib_name]
        ray_origin = mathutils.Vector((x, 0.0, deck_height))
        ray_direction = mathutils.Vector((0.0, 1.0, 0.0))
        inv_world = rib_obj.matrix_world.inverted()
        origin_local = inv_world @ ray_origin
        direction_local = inv_world.to_quaternion() @ ray_direction
        
        hit, loc, norm, index = rib_obj.ray_cast(origin_local, direction_local)
        if hit:
            world_loc = rib_obj.matrix_world @ loc
            beam_width = abs(world_loc.y)
            print(f"Found width {{beam_width}} for {{rib_name}} at Z={{deck_height}}")
        else:
            print(f"Missed {{rib_name}} at {{deck_height}}, checking rib height.")
            # If we miss, it might be that the rib is shorter than 6.0m at this point.
            # We should check the rib's top.
            # For now, use a reduced width or skip.
            beam_width = 0.0
    
    if beam_width > 0:
        # 1. Create Beam
        create_beam(f"Upper_Beam_{{i:02d}}", x, beam_width, deck_height, 0.25, "Rib_Material")
        
        # 2. Create Knees at each end
        create_knee(f"Upper_Knee_{{i:02d}}_R", x, beam_width, deck_height + 0.125, 0.6, 0.2, 'RIGHT', "Rib_Material")
        create_knee(f"Upper_Knee_{{i:02d}}_L", x, -beam_width, deck_height + 0.125, 0.6, 0.2, 'LEFT', "Rib_Material")

print(f"Created upper deck beams and knees.")
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
    create_upper_deck_beams_and_knees()
