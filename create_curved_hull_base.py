import socket
import json

def create_curved_hull_base():
    host = '127.0.0.1'
    port = 9876

    # Historical dimensions (real-size 1:1)
    keel_length = 37.9
    keel_width = 0.6
    keel_height = 0.8
    stem_height = 10.0
    stern_height = 8.0

    # Python code to execute in Blender
    code = f"""
import bpy
import mathutils
import math

def create_curved_beam(name, points, width, height, material_name):
    # 1. Create a curve
    curve_data = bpy.data.curves.new(name=name + "_Curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.fill_mode = 'FULL'
    curve_data.bevel_depth = 0.0 # We will use a mesh instead for better control of rectangular cross-section
    
    polyline = curve_data.splines.new('BEZIER')
    polyline.bezier_points.add(len(points) - 1)
    
    for i, p in enumerate(points):
        polyline.bezier_points[i].co = p
        polyline.bezier_points[i].handle_left_type = 'AUTO'
        polyline.bezier_points[i].handle_right_type = 'AUTO'
    
    curve_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(curve_obj)
    
    # 2. Convert to mesh with rectangular cross-section
    # We'll use a simple geometry node or a bevel object if needed, 
    # but for a "curvy" keel/stem/stern, a Bmesh sweep is more robust.
    
    bpy.context.view_layer.objects.active = curve_obj
    bpy.ops.object.convert(target='MESH')
    
    # After conversion, we have a line of vertices. We need to extrude it.
    # A better way for rectangular beams is to use a Curve with a "Square" bevel object
    return curve_obj

def create_rectangular_curved_beam(name, points, width, thickness, material_name):
    # Clean up existing
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    # Path points
    curve_data = bpy.data.curves.new(name + "_Path", type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for i, p in enumerate(points):
        spline.bezier_points[i].co = p
        spline.bezier_points[i].handle_left_type = 'AUTO'
        spline.bezier_points[i].handle_right_type = 'AUTO'
    
    path_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(path_obj)
    
    # Add thickness using extrude and bevel (which makes it a pipe/box)
    # For a rectangular beam:
    curve_data.fill_mode = 'FULL'
    curve_data.extrude = width / 2.0
    curve_data.bevel_depth = thickness / 2.0
    curve_data.bevel_resolution = 0 # 0 makes it square edges
    
    if material_name in bpy.data.materials:
        path_obj.data.materials.append(bpy.data.materials[material_name])
        
    return path_obj

# 1. Clean up old objects
for n in ["Keel", "Stempost", "Sternpost"]:
    if n in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)

# 2. Materials
if "Keel_Material" not in bpy.data.materials:
    mat = bpy.data.materials.new(name="Keel_Material")
    mat.diffuse_color = (0.1, 0.05, 0.0, 1.0)
else:
    mat = bpy.data.materials["Keel_Material"]

# 3. Create CURVED KEEL
# Points: Back (-18.95), Middle (0), Front (18.95)
# Keel has a slight upward curve (sheer) at the ends in some designs, 
# but mostly it's straight with the stem/stern curving off it.
# Schematic 20250821_115101 shows the keel is mostly straight, 
# but the stem (front) curves UP significantly.
keel_points = [
    (-18.95, 0, 0),
    (0, 0, -0.2), # Slight dip in middle or keep it 0
    (18.95, 0, 0)
]
keel = create_rectangular_curved_beam("Keel", keel_points, 0.6, 0.8, "Keel_Material")

# 4. Create CURVED STEMPOST (Front)
# Starts at (18.95, 0, 0)
# Curves forward and up
stem_points = [
    (18.95, 0, 0),
    (21.0, 0, 3.0),
    (23.0, 0, 10.0)
]
stem = create_rectangular_curved_beam("Stempost", stem_points, 0.6, 0.6, "Keel_Material")

# 5. Create CURVED STERNPOST (Back)
# Starts at (-18.95, 0, 0)
# Curves back and up
stern_points = [
    (-18.95, 0, 0),
    (-19.5, 0, 3.0),
    (-20.5, 0, 8.0)
]
stern = create_rectangular_curved_beam("Sternpost", stern_points, 0.6, 0.6, "Keel_Material")

print("Created curved Keel, Stempost, and Sternpost")
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
    create_curved_hull_base()
