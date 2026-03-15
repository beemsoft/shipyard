import socket
import json

def create_hull_ribs():
    host = '127.0.0.1'
    port = 9876

    # Real-size dimensions
    keel_length = 37.9
    half_length = keel_length / 2.0
    num_ribs = 15  # Number of ribs along one side
    rib_spacing = keel_length / (num_ribs - 1)

    # Python code for Blender
    code = f"""
import bpy
import mathutils
import math

def create_rib(name, x_pos, width_at_deck, height_at_deck, bilge_width, material_name):
    # Create a Bezier curve for a single rib (full-section)
    # Points define the U-shape of the hull section
    # (x, y, z) -> x is along keel, y is width, z is height
    
    # Get keel top Z at this X position
    keel_top_z = 0.0
    if "Keel" in bpy.data.objects:
        keel = bpy.data.objects["Keel"]
        ray_origin = mathutils.Vector((x_pos, 0.0, 10.0))
        ray_direction = mathutils.Vector((0.0, 0.0, -1.0))
        inv_world = keel.matrix_world.inverted()
        origin_local = inv_world @ ray_origin
        direction_local = inv_world.to_quaternion() @ ray_direction
        hit, loc, norm, index = keel.ray_cast(origin_local, direction_local)
        if hit:
            world_loc = keel.matrix_world @ loc
            keel_top_z = world_loc.z

    # Full U shape:
    # (-width_at_deck, height_at_deck + keel_top_z) -> (-bilge_width, 1.0 + keel_top_z) -> (0, keel_top_z) -> (bilge_width, 1.0 + keel_top_z) -> (width_at_deck, height_at_deck + keel_top_z)
    full_points = [
        (x_pos, -width_at_deck, height_at_deck + keel_top_z),
        (x_pos, -bilge_width, 1.0 + keel_top_z),
        (x_pos, 0.0, keel_top_z),
        (x_pos, bilge_width, 1.0 + keel_top_z),
        (x_pos, width_at_deck, height_at_deck + keel_top_z)
    ]
    
    curve_data = bpy.data.curves.new(name + "_Curve", type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(full_points) - 1)
    
    for i, p in enumerate(full_points):
        spline.bezier_points[i].co = p
        spline.bezier_points[i].handle_left_type = 'AUTO'
        spline.bezier_points[i].handle_right_type = 'AUTO'
        
    rib_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(rib_obj)
    
    # Use a bevel object for square shape
    # This bevel object is created in the main loop and passed or found
    if "Rib_Profile" in bpy.data.objects:
        curve_data.bevel_mode = 'OBJECT'
        curve_data.bevel_object = bpy.data.objects["Rib_Profile"]
        curve_data.use_fill_caps = True
    else:
        # Fallback to depth if profile not found
        curve_data.fill_mode = 'FULL'
        curve_data.bevel_depth = 0.2
        curve_data.bevel_resolution = 4
    
    if material_name in bpy.data.materials:
        rib_obj.data.materials.append(bpy.data.materials[material_name])
    
    return rib_obj

# Clean up existing ribs and the profile
for obj in bpy.data.objects:
    if obj.name.startswith("Rib_") or obj.name == "Rib_Profile":
        bpy.data.objects.remove(obj, do_unlink=True)
for curve in bpy.data.curves:
    if curve.name.startswith("Rib_") or curve.name == "Rib_Profile":
        bpy.data.curves.remove(curve, do_unlink=True)

# Create the square bevel profile
profile_size = 0.2
profile_curve = bpy.data.curves.new("Rib_Profile", type='CURVE')
profile_curve.dimensions = '2D'
spline = profile_curve.splines.new('POLY')
spline.use_cyclic_u = True
# Square centered at (0,0)
spline.points.add(3)
spline.points[0].co = (-profile_size/2, -profile_size/2, 0, 1)
spline.points[1].co = (profile_size/2, -profile_size/2, 0, 1)
spline.points[2].co = (profile_size/2, profile_size/2, 0, 1)
spline.points[3].co = (-profile_size/2, profile_size/2, 0, 1)

profile_obj = bpy.data.objects.new("Rib_Profile", profile_curve)
bpy.context.collection.objects.link(profile_obj)
profile_obj.hide_viewport = True
profile_obj.hide_render = True

# Material
if "Rib_Material" not in bpy.data.materials:
    mat = bpy.data.materials.new(name="Rib_Material")
    mat.diffuse_color = (0.2, 0.1, 0.05, 1.0) # Dark wood
else:
    mat = bpy.data.materials["Rib_Material"]

# Rib parameters - varying width and height along the hull
# Center is wider, ends are narrower
# User wants ribs BETWEEN the posts. Stempost is at X=18.95, Sternpost at X=-18.95.
# Let's place ribs between X = -17.5 and X = 17.5 to ensure they are between the posts.
num_ribs = {num_ribs}
start_x = -17.5
end_x = 17.5
rib_range = end_x - start_x
spacing = rib_range / (num_ribs - 1)

for i in range(num_ribs):
    x = start_x + (i * spacing)
    
    # Calculate profile based on position (elliptical-ish)
    # normalized position from -1 to 1 based on keel half length
    t = x / {half_length}
    factor = math.sqrt(max(0, 1 - t**2)) # 1 at center, 0 at ends
    
    # Base dimensions for 'De Zeven Provinciën'
    # The ship's width was about 40 Amsterdam feet (approx 12 meters)
    # The height from keel to upper deck varied, but we'll aim for approx 9-10 meters.
    max_width = 7.0
    max_height = 8.0
    
    width = 3.5 + (max_width - 3.5) * factor
    height = 5.0 + (max_height - 5.0) * factor
    bilge = width * 0.85
    
    create_rib(f"Rib_{{i:02d}}", x, width, height, bilge, "Rib_Material")

print(f"Created {{num_ribs}} hull ribs.")
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
    create_hull_ribs()
