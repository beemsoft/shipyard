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
    # Create a Bezier curve for a single rib (half-section)
    # Points define the U-shape of the hull section
    # (x, y, z) -> x is along keel, y is width, z is height
    
    # We create a point at the keel (0,0), then a bilge point, then a deck point
    points = [
        (x_pos, 0.0, 0.0),             # Keel
        (x_pos, bilge_width, 1.0),     # Bilge (turn of the bilge)
        (x_pos, width_at_deck, height_at_deck) # Deck level
    ]
    
    curve_data = bpy.data.curves.new(name + "_Curve", type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    
    for i, p in enumerate(points):
        spline.bezier_points[i].co = p
        spline.bezier_points[i].handle_left_type = 'AUTO'
        spline.bezier_points[i].handle_right_type = 'AUTO'
    
    # Mirror the rib to the other side
    # We can use a mirror modifier later, but for now let's just make it symmetric in the curve
    # or create a full U shape
    
    # Full U shape:
    # (-width_at_deck, height_at_deck) -> (-bilge_width, 1.0) -> (0,0) -> (bilge_width, 1.0) -> (width_at_deck, height_at_deck)
    full_points = [
        (x_pos, -width_at_deck, height_at_deck),
        (x_pos, -bilge_width, 1.0),
        (x_pos, 0.0, 0.0),
        (x_pos, bilge_width, 1.0),
        (x_pos, width_at_deck, height_at_deck)
    ]
    
    # Re-setup spline with full points
    spline.bezier_points.add(len(full_points) - len(points))
    for i, p in enumerate(full_points):
        spline.bezier_points[i].co = p
        spline.bezier_points[i].handle_left_type = 'AUTO'
        spline.bezier_points[i].handle_right_type = 'AUTO'
        
    rib_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(rib_obj)
    
    # Add some thickness
    curve_data.fill_mode = 'FULL'
    curve_data.bevel_depth = 0.2
    curve_data.bevel_resolution = 4
    
    if material_name in bpy.data.materials:
        rib_obj.data.materials.append(bpy.data.materials[material_name])
    
    return rib_obj

# Clean up existing ribs
for obj in bpy.data.objects:
    if obj.name.startswith("Rib_"):
        bpy.data.objects.remove(obj, do_unlink=True)

# Material
if "Rib_Material" not in bpy.data.materials:
    mat = bpy.data.materials.new(name="Rib_Material")
    mat.diffuse_color = (0.2, 0.1, 0.05, 1.0) # Dark wood
else:
    mat = bpy.data.materials["Rib_Material"]

# Rib parameters - varying width and height along the hull
# Center is wider, ends are narrower
half_len = {half_length}
num_ribs = {num_ribs}
for i in range(num_ribs):
    x = -half_len + (i * {rib_spacing})
    
    # Calculate profile based on position (elliptical-ish)
    # normalized position from -1 to 1
    t = x / half_len
    factor = math.sqrt(max(0, 1 - t**2)) # 1 at center, 0 at ends
    
    # Base dimensions
    max_width = 7.0
    max_height = 8.0
    
    width = 1.5 + (max_width - 1.5) * factor
    height = 3.0 + (max_height - 3.0) * factor
    bilge = width * 0.8
    
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
