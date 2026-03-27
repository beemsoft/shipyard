import socket
import json

def fit_beams_and_knees_to_all_frames():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import mathutils
import math

def create_beam(name, x, width, z, thickness, material_name, collection_name):
    # A simple rectangular beam across the ship
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    if collection_name not in bpy.data.collections:
        coll = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(coll)
    else:
        coll = bpy.data.collections[collection_name]
    
    coll.objects.link(obj)
    
    # Vertices for a box: thickness x (2 * width) x thickness
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

def create_knee(name, x, y, z, size, thickness, orientation, material_name, collection_name):
    # Create an L-shaped "knee" at (x, y, z)
    # orientation: 'LEFT' or 'RIGHT'
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    if collection_name not in bpy.data.collections:
        coll = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(coll)
    else:
        coll = bpy.data.collections[collection_name]
    
    coll.objects.link(obj)
    
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

# Clean up existing beams and knees
collections_to_clean = ["Lower_Deck_Beams", "Middle_Deck_Beams", "Upper_Deck_Beams", "Stern_Deck_Beams"]
for coll_name in collections_to_clean:
    if coll_name in bpy.data.collections:
        coll = bpy.data.collections[coll_name]
        for obj in list(coll.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

# Find all hull frames
frames = []
for obj in bpy.data.objects:
    if obj.name.startswith("Rib_") or obj.name.startswith("Stern_Frame_"):
        # Get X position from first point of spline
        if hasattr(obj.data, 'splines') and len(obj.data.splines) > 0 and len(obj.data.splines[0].bezier_points) > 0:
            x_pos = obj.data.splines[0].bezier_points[0].co.x
            frames.append((x_pos, obj))

# Sort frames by X position (front to back)
frames.sort(key=lambda x: x[0], reverse=True)

def get_keel_top_z(x):
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
            return world_loc.z
    return 0.0

def get_beam_width(frame_obj, x, z_height):
    ray_origin = mathutils.Vector((x, 0.0, z_height))
    ray_direction = mathutils.Vector((0.0, 1.0, 0.0))
    inv_world = frame_obj.matrix_world.inverted()
    origin_local = inv_world @ ray_origin
    direction_local = inv_world.to_quaternion() @ ray_direction
    hit, loc, norm, index = frame_obj.ray_cast(origin_local, direction_local)
    if hit:
        world_loc = frame_obj.matrix_world @ loc
        return abs(world_loc.y)
    return 0.0

for i, (x, frame_obj) in enumerate(frames):
    keel_z = get_keel_top_z(x)
    
    # 1. Lower Deck (standard height)
    lower_deck_z = keel_z + 3.0
    width_lower = get_beam_width(frame_obj, x, lower_deck_z)
    if width_lower > 0.1:
        create_beam(f"Lower_Beam_{i:02d}", x, width_lower, lower_deck_z, 0.25, "Rib_Material", "Lower_Deck_Beams")
        create_knee(f"Lower_Knee_{i:02d}_R", x, width_lower, lower_deck_z + 0.125, 0.7, 0.2, 'RIGHT', "Rib_Material", "Lower_Deck_Beams")
        create_knee(f"Lower_Knee_{i:02d}_L", x, -width_lower, lower_deck_z + 0.125, 0.7, 0.2, 'LEFT', "Rib_Material", "Lower_Deck_Beams")

    # 2. Middle Deck
    middle_deck_z = keel_z + 5.0
    width_middle = get_beam_width(frame_obj, x, middle_deck_z)
    if width_middle > 0.1:
        create_beam(f"Middle_Beam_{i:02d}", x, width_middle, middle_deck_z, 0.25, "Rib_Material", "Middle_Deck_Beams")
        create_knee(f"Middle_Knee_{i:02d}_R", x, width_middle, middle_deck_z + 0.125, 0.65, 0.2, 'RIGHT', "Rib_Material", "Middle_Deck_Beams")
        create_knee(f"Middle_Knee_{i:02d}_L", x, -width_middle, middle_deck_z + 0.125, 0.65, 0.2, 'LEFT', "Rib_Material", "Middle_Deck_Beams")

    # 3. Upper Deck (standard height)
    upper_deck_z = keel_z + 7.0
    width_upper = get_beam_width(frame_obj, x, upper_deck_z)
    if width_upper > 0.1:
        create_beam(f"Upper_Beam_{i:02d}", x, width_upper, upper_deck_z, 0.25, "Rib_Material", "Upper_Deck_Beams")
        create_knee(f"Upper_Knee_{i:02d}_R", x, width_upper, upper_deck_z + 0.125, 0.6, 0.2, 'RIGHT', "Rib_Material", "Upper_Deck_Beams")
        create_knee(f"Upper_Knee_{i:02d}_L", x, -width_upper, upper_deck_z + 0.125, 0.6, 0.2, 'LEFT', "Rib_Material", "Upper_Deck_Beams")

    # 4. Stern Decks (Quarterdeck and Poop)
    # Implementing slight upward slope towards the stern (negative X)
    # Slope starts from X = -5.0
    slope_factor = 0.0
    if x < -5.0:
        slope_factor = abs(x + 5.0) * 0.15  # 15cm rise per meter
        
    if x < -5.0:
        quarter_z = keel_z + 9.0 + slope_factor
        width_q = get_beam_width(frame_obj, x, quarter_z)
        if width_q > 0.1:
            create_beam(f"Quarter_Beam_{i:02d}", x, width_q, quarter_z, 0.25, "Rib_Material", "Stern_Deck_Beams")
            create_knee(f"Quarter_Knee_{i:02d}_R", x, width_q, quarter_z + 0.125, 0.5, 0.2, 'RIGHT', "Rib_Material", "Stern_Deck_Beams")
            create_knee(f"Quarter_Knee_{i:02d}_L", x, -width_q, quarter_z + 0.125, 0.5, 0.2, 'LEFT', "Rib_Material", "Stern_Deck_Beams")
            
    if x < -12.0:
        # Poop deck also inherits the slope
        poop_z = keel_z + 11.5 + slope_factor
        width_p = get_beam_width(frame_obj, x, poop_z)
        if width_p > 0.1:
            create_beam(f"Poop_Beam_{i:02d}", x, width_p, poop_z, 0.25, "Rib_Material", "Stern_Deck_Beams")
            create_knee(f"Poop_Knee_{i:02d}_R", x, width_p, poop_z + 0.125, 0.4, 0.2, 'RIGHT', "Rib_Material", "Stern_Deck_Beams")
            create_knee(f"Poop_Knee_{i:02d}_L", x, -width_p, poop_z + 0.125, 0.4, 0.2, 'LEFT', "Rib_Material", "Stern_Deck_Beams")

print(f"Fitted beams and knees to {len(frames)} frames across multiple deck levels.")
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
    fit_beams_and_knees_to_all_frames()
