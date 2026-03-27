import socket
import json

def create_quarterdeck_poop_frames():
    host = '127.0.0.1'
    port = 9876

    # Parameters for 'De Zeven Provinciën'
    # Keel length: 37.9 (X: -18.95 to 18.95)
    # Existing ribs are from X: -17.5 to 17.5
    # Sternpost at X: -18.95 (bottom), X: -21.45 (top at Z=10.4)

    # We want more frames at the stern for quarterdeck (half-deck) and poop.
    # Quarterdeck usually starts around the middle and goes to the stern.
    # Poop deck is even higher and further back.

    code = """
import bpy
import mathutils
import math

def create_stern_frame(name, x_pos, width_at_deck, height_at_deck, bilge_width, tumblehome_offset, material_name):
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
        elif x_pos < -18.95: # Behind the keel, follow the sternpost if possible
             if "Sternpost" in bpy.data.objects:
                sternpost = bpy.data.objects["Sternpost"]
                inv_world_s = sternpost.matrix_world.inverted()
                origin_local_s = inv_world_s @ ray_origin
                direction_local_s = inv_world_s.to_quaternion() @ ray_direction
                hit_s, loc_s, norm_s, index_s = sternpost.ray_cast(origin_local_s, direction_local_s)
                if hit_s:
                    world_loc_s = sternpost.matrix_world @ loc_s
                    keel_top_z = world_loc_s.z

    # Split into 2 curves: 1 Hollow (lower) and 1 Tumblehome (upper)
    # The breadth (widest point) is the transition between them.
    breadth_z = 3.0 + keel_top_z
    breadth_y = bilge_width * 1.1

    # 1. Lower Hollow Curve (Hollow below) - SHARP INWARD HOLLOW shape
    # Adjusting points to be closer to the center line (smaller Y) to force an inward curve.
    hollow_points = [
        (x_pos, -breadth_y, breadth_z),  # Top of hollow (breadth)
        (x_pos, -(bilge_width * 0.9), 0.8 + keel_top_z),  # Mid hollow - Lower and wider
        (x_pos, -(bilge_width * 0.5), 0.1 + keel_top_z),  # Lower hollow - Closer to keel but still wider
        (x_pos, 0.0, keel_top_z),  # Keel
        (x_pos, (bilge_width * 0.5), 0.1 + keel_top_z),   # Lower hollow
        (x_pos, (bilge_width * 0.9), 0.8 + keel_top_z),   # Mid hollow
        (x_pos, breadth_y, breadth_z)     # Top of hollow (breadth)
    ]

    # 2. Upper Tumblehome Curve (Tumblehome above)
    tumblehome_points_l = [
        (x_pos, -breadth_y, breadth_z),  # Bottom of tumblehome (breadth)
        (x_pos, -width_at_deck, height_at_deck + keel_top_z)
    ]
    tumblehome_points_r = [
        (x_pos, breadth_y, breadth_z),
        (x_pos, width_at_deck, height_at_deck + keel_top_z)
    ]

    def create_curve(curve_name, points, mat_name, sharp_keel=False, upper_tumble=False):
        curve_data = bpy.data.curves.new(curve_name + "_Curve", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(len(points) - 1)
        for i, p in enumerate(points):
            spline.bezier_points[i].co = p
            if sharp_keel and i == (len(points) // 2): # The keel point
                spline.bezier_points[i].handle_left_type = 'VECTOR'
                spline.bezier_points[i].handle_right_type = 'VECTOR'
            elif upper_tumble:
                # For upper tumblehome, use ALIGNED to keep it slightly more vertical at the breadth
                spline.bezier_points[i].handle_left_type = 'ALIGNED'
                spline.bezier_points[i].handle_right_type = 'ALIGNED'
            else:
                spline.bezier_points[i].handle_left_type = 'AUTO'
                spline.bezier_points[i].handle_right_type = 'AUTO'
        obj = bpy.data.objects.new(curve_name, curve_data)
        
        if "Hull_Stern_Frames" not in bpy.data.collections:
            stern_coll = bpy.data.collections.new("Hull_Stern_Frames")
            bpy.context.scene.collection.children.link(stern_coll)
        else:
            stern_coll = bpy.data.collections["Hull_Stern_Frames"]
        stern_coll.objects.link(obj)

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

    # Create the three segments for the frame
    hollow_obj = create_curve(name + "_Hollow", hollow_points, material_name, sharp_keel=True)
    tumble_l_obj = create_curve(name + "_Tumble_L", tumblehome_points_l, material_name)
    tumble_r_obj = create_curve(name + "_Tumble_R", tumblehome_points_r, material_name)
    
    return [hollow_obj, tumble_l_obj, tumble_r_obj]

# Clean up existing stern frames and overlapping ribs
if "Hull_Stern_Frames" in bpy.data.collections:
    coll = bpy.data.collections["Hull_Stern_Frames"]
    for obj in coll.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

# Remove any Rib_ objects that overlap with the new stern frame positions
# Stern frames start at X = -5 and go backwards. 
# Ribs from create_hull_ribs.py are named Rib_00, Rib_01, etc.
for obj in list(bpy.data.objects):
    if obj.name.startswith("Rib_"):
        # Check X position
        x_pos = obj.location.x
        # For curves, we should check the points if location is not set
        if hasattr(obj.data, 'splines') and len(obj.data.splines) > 0 and len(obj.data.splines[0].bezier_points) > 0:
             x_pos = obj.data.splines[0].bezier_points[0].co.x
             if x_pos <= -5.0:
                  bpy.data.objects.remove(obj, do_unlink=True)
        elif x_pos <= -5.0:
             bpy.data.objects.remove(obj, do_unlink=True)

# Stern frames parameters
# We add frames from X = -5 to X = -20.5 (slightly beyond sternpost start)
# frames_data: (x_pos, width, height, bilge, tumblehome_offset)
# tumblehome_offset: positive means the middle point is further out than the top
# REDUCING tumblehome_offset to make the top less curved inward
# INCREASING heights to match higher poop deck from schematic
frames_data = [
    (-5.0,  6.8, 9.5,  5.8, 0.2),
    (-8.0,  6.4, 9.6,  5.4, 0.3),
    (-11.0, 5.8, 10.0,  4.8, 0.4), # Quarterdeck starts
    (-14.0, 5.0, 11.0,  4.0, 0.5), # Quarterdeck
    (-17.0, 3.8, 12.5, 3.0, 0.6), # Towards the poop deck
    (-18.5, 3.0, 13.5, 2.2, 0.7), # Poop deck area
    (-19.5, 2.2, 14.2, 1.5, 0.8), # Further back, sharp S-curve
    (-20.5, 1.5, 15.0, 1.0, 1.0)  # Far stern, very narrow at bottom
]

for i, (x, w, h, b, t) in enumerate(frames_data):
    create_stern_frame(f"Stern_Frame_{i:02d}", x, w, h, b, t, "Rib_Material")

print(f"Created {len(frames_data)} stern frames for quarterdeck and poop.")
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
    create_quarterdeck_poop_frames()
