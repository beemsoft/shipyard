import socket
import json

def correct_rib_beams():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import mathutils
import math

def create_beam(name, x, width, z, thickness, material_name):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
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
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    s = size
    t = thickness
    if orientation == 'RIGHT':
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
        (0,1,2,3,4,5), (6,7,8,9,10,11),
        (0,6,7,1), (1,7,8,2), (2,8,9,3), (3,9,10,4), (4,10,11,5), (5,11,6,0)
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    if material_name in bpy.data.materials:
        obj.data.materials.append(bpy.data.materials[material_name])
    return obj

def get_keel_top_z(x):
    keel_top_z = 0.0
    if "Keel" in bpy.data.objects:
        keel = bpy.data.objects["Keel"]
        ray_origin = mathutils.Vector((x, 0.0, 15.0))
        ray_direction = mathutils.Vector((0.0, 0.0, -1.0))
        inv_world = keel.matrix_world.inverted()
        origin_local = inv_world @ ray_origin
        direction_local = inv_world.to_quaternion() @ ray_direction
        hit, loc, norm, index = keel.ray_cast(origin_local, direction_local)
        if hit:
            world_loc = keel.matrix_world @ loc
            keel_top_z = world_loc.z
        elif x > 18.95:
             if "Stempost" in bpy.data.objects:
                stempost = bpy.data.objects["Stempost"]
                inv_world_s = stempost.matrix_world.inverted()
                origin_local_s = inv_world_s @ ray_origin
                direction_local_s = inv_world_s.to_quaternion() @ ray_direction
                hit_s, loc_s, norm_s, index_s = stempost.ray_cast(origin_local_s, direction_local_s)
                if hit_s:
                    world_loc_s = stempost.matrix_world @ loc_s
                    keel_top_z = world_loc_s.z
    return keel_top_z

def get_beam_width(x, z, frame_name_pattern):
    # Find all objects matching the pattern and try ray-casting
    # We'll try to find the width on the RIGHT side (y > 0)
    width = 0.0
    candidates = [obj for obj in bpy.data.objects if frame_name_pattern in obj.name]
    
    for obj in candidates:
        if obj.type != 'MESH' and obj.type != 'CURVE':
            continue
            
        try:
            ray_origin = mathutils.Vector((x, 0.0, z))
            ray_direction = mathutils.Vector((0.0, 1.0, 0.0))
            inv_world = obj.matrix_world.inverted()
            origin_local = inv_world @ ray_origin
            direction_local = inv_world.to_quaternion() @ ray_direction
            
            hit, loc, norm, index = obj.ray_cast(origin_local, direction_local)
            if hit:
                world_loc = obj.matrix_world @ loc
                width = abs(world_loc.y)
                return width
                
            # Try outside-in if center-out misses
            ray_origin_out = mathutils.Vector((x, 20.0, z))
            ray_direction_in = mathutils.Vector((0.0, -1.0, 0.0))
            origin_local_out = inv_world @ ray_origin_out
            direction_local_in = inv_world.to_quaternion() @ ray_direction_in
            hit_in, loc_in, norm_in, index_in = obj.ray_cast(origin_local_out, direction_local_in)
            if hit_in:
                world_loc_in = obj.matrix_world @ loc_in
                width = abs(world_loc_in.y)
                return width
        except Exception:
            continue
            
    return width

# 1. Clean up existing beams and knees
prefixes = ["Lower_Beam", "Upper_Beam", "Quarterdeck_Beam", "Poop_Beam", "Forecastle_Beam",
            "Lower_Knee", "Upper_Knee", "Quarterdeck_Knee", "Poop_Knee", "Forecastle_Knee",
            "Knee_", "Middle_Beam", "Middle_Knee"]
for obj in list(bpy.data.objects):
    for pref in prefixes:
        if obj.name.startswith(pref):
            bpy.data.objects.remove(obj, do_unlink=True)
            break
for mesh in list(bpy.data.meshes):
    for pref in prefixes:
        if mesh.name.startswith(pref):
            bpy.data.meshes.remove(mesh, do_unlink=True)
            break

# 2. Define Decks and their ranges
# Lower deck: All ribs (full length)
# Upper deck: All ribs (full length)
# Quarterdeck: Stern area to mid (X < 5.0)
# Poop: Stern area (X < -10.0)
# Forecastle: Bow area (X > -5.0)

# Ribs: Rib_00 to Rib_14, start_x = -17.5, end_x = 17.5
num_ribs = 15
start_x = -17.5
end_x = 17.5
spacing = (end_x - start_x) / (num_ribs - 1)

# Heights (relative to keel top)
H_LOWER = 3.5
H_UPPER = 5.0
H_QUARTER = 6.0
H_POOP = 7.0
H_FORE = 6.0

# Beams thickness
T = 0.25

for i in range(num_ribs):
    x = start_x + (i * spacing)
    kz = get_keel_top_z(x)
    rib_name = f"Rib_{i:02d}"
    
    # Lower Deck
    w_low = get_beam_width(x, kz + H_LOWER, rib_name)
    if w_low > 0:
        create_beam(f"Lower_Beam_{i:02d}", x, w_low, kz + H_LOWER, T, "Rib_Material")
        create_knee(f"Lower_Knee_{i:02d}_R", x, w_low, kz + H_LOWER + 0.125, 0.8, 0.2, 'RIGHT', "Rib_Material")
        create_knee(f"Lower_Knee_{i:02d}_L", x, -w_low, kz + H_LOWER + 0.125, 0.8, 0.2, 'LEFT', "Rib_Material")
    
    # Upper Deck
    w_up = get_beam_width(x, kz + H_UPPER, rib_name)
    if w_up > 0:
        create_beam(f"Upper_Beam_{i:02d}", x, w_up, kz + H_UPPER, T, "Rib_Material")
        create_knee(f"Upper_Knee_{i:02d}_R", x, w_up, kz + H_UPPER + 0.125, 0.6, 0.2, 'RIGHT', "Rib_Material")
        create_knee(f"Upper_Knee_{i:02d}_L", x, -w_up, kz + H_UPPER + 0.125, 0.6, 0.2, 'LEFT', "Rib_Material")
    
    # Forecastle Deck (Forward ribs and frames)
    if x > -5.0:
        w_fore = get_beam_width(x, kz + H_FORE, rib_name)
        if w_fore == 0: # Try Forecastle Frame name pattern if within Rib X but Rib miss
             w_fore = get_beam_width(x, kz + H_FORE, "Forecastle_Frame")
        if w_fore > 0:
            create_beam(f"Forecastle_Beam_{i:02d}", x, w_fore, kz + H_FORE, T, "Rib_Material")
            create_knee(f"Forecastle_Knee_{i:02d}_R", x, w_fore, kz + H_FORE + 0.125, 0.6, 0.18, 'RIGHT', "Rib_Material")
            create_knee(f"Forecastle_Knee_{i:02d}_L", x, -w_fore, kz + H_FORE + 0.125, 0.6, 0.18, 'LEFT', "Rib_Material")
            print(f"Created Forecastle_Beam_{i:02d} at X={x}, width={w_fore}")

    # Quarterdeck (Aft ribs and frames)
    if x < 5.0:
        w_quarter = get_beam_width(x, kz + H_QUARTER, rib_name)
        if w_quarter == 0:
            w_quarter = get_beam_width(x, kz + H_QUARTER, "Stern_Frame")
        if w_quarter > 0:
            create_beam(f"Quarterdeck_Beam_{i:02d}", x, w_quarter, kz + H_QUARTER, T, "Rib_Material")
            create_knee(f"Quarterdeck_Knee_{i:02d}_R", x, w_quarter, kz + H_QUARTER + 0.125, 0.6, 0.18, 'RIGHT', "Rib_Material")
            create_knee(f"Quarterdeck_Knee_{i:02d}_L", x, -w_quarter, kz + H_QUARTER + 0.125, 0.6, 0.18, 'LEFT', "Rib_Material")
            print(f"Created Quarterdeck_Beam_{i:02d} at X={x}, width={w_quarter}")

    # Poop Deck (Further aft ribs and frames)
    if x < -10.0:
        w_poop = get_beam_width(x, kz + H_POOP, rib_name)
        if w_poop == 0:
            w_poop = get_beam_width(x, kz + H_POOP, "Stern_Frame")
        if w_poop > 0:
            create_beam(f"Poop_Beam_{i:02d}", x, w_poop, kz + H_POOP, T, "Rib_Material")
            create_knee(f"Poop_Knee_{i:02d}_R", x, w_poop, kz + H_POOP + 0.125, 0.5, 0.18, 'RIGHT', "Rib_Material")
            create_knee(f"Poop_Knee_{i:02d}_L", x, -w_poop, kz + H_POOP + 0.125, 0.5, 0.18, 'LEFT', "Rib_Material")
            print(f"Created Poop_Beam_{i:02d} at X={x}, width={w_poop}")

# 3. Handle specific Forecastle and Stern frames if they exist and are not covered by Ribs
# Forecastle frames: Forecastle_Frame_00 to 07
for j in range(8):
    fx = [5.0, 8.0, 11.0, 14.0, 17.0, 19.0, 21.0, 23.0][j]
    if fx > 17.5: # Only if beyond the last Rib
        kz = get_keel_top_z(fx)
        fname = f"Forecastle_Frame_{j:02d}"
        w_fore = get_beam_width(fx, kz + H_FORE, fname)
        if w_fore > 0:
            create_beam(f"Forecastle_Beam_F{j:02d}", fx, w_fore, kz + H_FORE, T, "Rib_Material")
            create_knee(f"Forecastle_Knee_F{j:02d}_R", fx, w_fore, kz + H_FORE + 0.125, 0.6, 0.18, 'RIGHT', "Rib_Material")
            create_knee(f"Forecastle_Knee_F{j:02d}_L", fx, -w_fore, kz + H_FORE + 0.125, 0.6, 0.18, 'LEFT', "Rib_Material")

# Note: Stern Frames were removed in the previous step, so we stick to Ribs for now.
# If they are recreated later, this script can be extended.

print("Corrected rib beams for all decks.")
"""

    try:
        with socket.create_connection((host, port), timeout=60) as s:
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
    correct_rib_beams()
