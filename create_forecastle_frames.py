import socket
import json

def create_forecastle_frames():
    host = '127.0.0.1'
    port = 9876

    # Parameters for 'De Zeven Provinciën'
    # Keel length: 37.9 (X: -18.95 to 18.95)
    # Existing ribs are from X: -17.5 to 17.5
    # Rib_14 is at X=17.5
    # Stempost starts at X=18.95 and curves forward.

    code = """
import bpy
import mathutils
import math

def create_bow_frame(name, x_pos, width_at_deck, height_at_deck, bilge_width, material_name):
    # Get keel top Z at this X position
    keel_top_z = 0.0
    if "Keel" in bpy.data.objects:
        keel = bpy.data.objects["Keel"]
        ray_origin = mathutils.Vector((x_pos, 0.0, 15.0))
        ray_direction = mathutils.Vector((0.0, 0.0, -1.0))
        inv_world = keel.matrix_world.inverted()
        origin_local = inv_world @ ray_origin
        direction_local = inv_world.to_quaternion() @ ray_direction
        hit, loc, norm, index = keel.ray_cast(origin_local, direction_local)
        if hit:
            world_loc = keel.matrix_world @ loc
            keel_top_z = world_loc.z
        elif x_pos > 18.95: # Ahead of the keel, follow the stempost
             if "Stempost" in bpy.data.objects:
                stempost = bpy.data.objects["Stempost"]
                inv_world_s = stempost.matrix_world.inverted()
                origin_local_s = inv_world_s @ ray_origin
                direction_local_s = inv_world_s.to_quaternion() @ ray_direction
                hit_s, loc_s, norm_s, index_s = stempost.ray_cast(origin_local_s, direction_local_s)
                if hit_s:
                    world_loc_s = stempost.matrix_world @ loc_s
                    keel_top_z = world_loc_s.z

    # Split into segments similar to stern frames
    # Breadth (widest point)
    breadth_z = 4.0 + keel_top_z
    breadth_y = bilge_width * 1.1

    # 1. Lower Curve (Hollow below for bow)
    hollow_points = [
        (x_pos, -breadth_y, breadth_z),
        (x_pos, -(bilge_width * 0.95), 1.5 + keel_top_z),
        (x_pos, -(bilge_width * 0.4), 0.2 + keel_top_z),
        (x_pos, 0.0, keel_top_z),
        (x_pos, (bilge_width * 0.4), 0.2 + keel_top_z),
        (x_pos, (bilge_width * 0.95), 1.5 + keel_top_z),
        (x_pos, breadth_y, breadth_z)
    ]

    # 2. Upper Curve (Flare for bow)
    flare_points_l = [
        (x_pos, -breadth_y, breadth_z),
        (x_pos, -width_at_deck, height_at_deck + keel_top_z)
    ]
    flare_points_r = [
        (x_pos, breadth_y, breadth_z),
        (x_pos, width_at_deck, height_at_deck + keel_top_z)
    ]

    def create_curve(curve_name, points, mat_name, sharp_keel=False):
        curve_data = bpy.data.curves.new(curve_name + "_Curve", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(len(points) - 1)
        for i, p in enumerate(points):
            spline.bezier_points[i].co = p
            if sharp_keel and i == (len(points) // 2):
                spline.bezier_points[i].handle_left_type = 'VECTOR'
                spline.bezier_points[i].handle_right_type = 'VECTOR'
            else:
                spline.bezier_points[i].handle_left_type = 'AUTO'
                spline.bezier_points[i].handle_right_type = 'AUTO'
        obj = bpy.data.objects.new(curve_name, curve_data)
        
        if "Forecastle_Frames" not in bpy.data.collections:
            coll = bpy.data.collections.new("Forecastle_Frames")
            bpy.context.scene.collection.children.link(coll)
        else:
            coll = bpy.data.collections["Forecastle_Frames"]
        coll.objects.link(obj)

        if "Rib_Profile" in bpy.data.objects:
            curve_data.bevel_mode = 'OBJECT'
            curve_data.bevel_object = bpy.data.objects["Rib_Profile"]
            curve_data.use_fill_caps = True
        else:
            curve_data.fill_mode = 'FULL'
            curve_data.bevel_depth = 0.2
        
        if mat_name in bpy.data.materials:
            obj.data.materials.append(bpy.data.materials[mat_name])
        return obj

    hollow_obj = create_curve(name + "_Hollow", hollow_points, material_name, sharp_keel=True)
    flare_l_obj = create_curve(name + "_Flare_L", flare_points_l, material_name)
    flare_r_obj = create_curve(name + "_Flare_R", flare_points_r, material_name)
    
    return [hollow_obj, flare_l_obj, flare_r_obj]

# Clean up
if "Forecastle_Frames" in bpy.data.collections:
    coll = bpy.data.collections["Forecastle_Frames"]
    for obj in coll.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

# Remove overlapping ribs at the bow (X > 5.0)
for obj in list(bpy.data.objects):
    if obj.name.startswith("Rib_"):
        x_pos = 0
        if hasattr(obj.data, 'splines') and len(obj.data.splines) > 0 and len(obj.data.splines[0].bezier_points) > 0:
             x_pos = obj.data.splines[0].bezier_points[0].co.x
        else:
             x_pos = obj.location.x
             
        if x_pos >= 5.0:
             bpy.data.objects.remove(obj, do_unlink=True)

# Forecastle frames parameters
# X positions: 5.0 to approx 23.0
# Forecastle deck is typically around 8.5m above keel (similar to quarterdeck)
# (x_pos, width, height, bilge)
frames_data = [
    (5.0,  6.8, 8.2,  5.8),
    (8.0,  6.5, 8.4,  5.4),
    (11.0, 6.0, 8.8,  4.8),
    (14.0, 5.2, 9.4,  4.0),
    (17.0, 4.2, 10.2, 3.2),
    (19.0, 3.5, 11.0, 2.5), # Above front of keel
    (21.0, 2.5, 12.0, 1.8), # Above stempost
    (23.0, 1.5, 13.0, 1.0)  # Near front tip of forecastle
]

for i, (x, w, h, b) in enumerate(frames_data):
    create_bow_frame(f"Forecastle_Frame_{i:02d}", x, w, h, b, "Rib_Material")

print(f"Created {len(frames_data)} forecastle frames.")
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
    create_forecastle_frames()
