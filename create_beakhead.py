import socket
import json

def create_beakhead():
    host = '127.0.0.1'
    port = 9876

    # The beakhead should be a separate massive beam
    # that has no gap with the underlying supporting beam (knee of the head).

    code = """
import bpy
import mathutils
import math

# 1. Cleanup
for obj in bpy.data.objects:
    if obj.name.startswith("Beakhead") or obj.name.startswith("Bowsprit_Support"):
        bpy.data.objects.remove(obj, do_unlink=True)
for mesh in bpy.data.meshes:
    if mesh.name.startswith("Beakhead") or mesh.name.startswith("Bowsprit_Support"):
        bpy.data.meshes.remove(mesh)
for curve in bpy.data.curves:
    if curve.name.startswith("Beakhead") or curve.name.startswith("Bowsprit_Support"):
        bpy.data.curves.remove(curve)

# 2. Bowsprit Support
x_support = 23.5
z_support_base = 8.5
height_support = 8.0 # Increased height
thickness = 0.6
width = 0.8

bpy.ops.mesh.primitive_cube_add(location=(x_support, 0, z_support_base + height_support/2))
support = bpy.context.active_object
support.name = "Bowsprit_Support"
support.scale = (thickness/2, width/2, height_support/2)
bpy.ops.object.transform_apply(scale=True)

# 3. Multiple Beakhead Beams (Stacked Scheg)
# The beakhead (scheg) consists of multiple curved timbers stacked together.
# We define 3 stacked beams following a similar curve.

beak_points_base = [
    (24.5, 0.0, 8.5),     # Starting near bowsprit support
    (26.0, 0.0, 10.5),
    (28.0, 0.0, 12.5),
    (30.0, 0.0, 14.5),
    (32.0, 0.0, 16.5),
    (33.5, 0.0, 18.5)
]

# Rectangular profile for the beams
p_x = 0.55
p_y = 0.75
if "Beak_Profile" not in bpy.data.objects:
    p_curve = bpy.data.curves.new("Beak_Profile", type='CURVE')
    p_curve.dimensions = '2D'
    p_spline = p_curve.splines.new('POLY')
    p_spline.use_cyclic_u = True
    p_spline.points.add(3)
    p_spline.points[0].co = (-p_x/2, -p_y/2, 0, 1)
    p_spline.points[1].co = (p_x/2, -p_y/2, 0, 1)
    p_spline.points[2].co = (p_x/2, p_y/2, 0, 1)
    p_spline.points[3].co = (-p_x/2, p_y/2, 0, 1)
    p_obj = bpy.data.objects.new("Beak_Profile", p_curve)
    bpy.context.collection.objects.link(p_obj)
    p_obj.hide_viewport = True
    p_obj.hide_render = True

for j in range(3):
    # Each beam slightly offset in Z to show they are separate
    z_offset = j * 0.76  # Stacked on top of each other
    points_j = [(p[0], p[1], p[2] + z_offset) for p in beak_points_base]
    
    curve_data = bpy.data.curves.new(f"Beakhead_Beam_{j}_Path", type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points_j) - 1)
    
    for i, p in enumerate(points_j):
        spline.bezier_points[i].co = p
        spline.bezier_points[i].handle_left_type = 'AUTO'
        spline.bezier_points[i].handle_right_type = 'AUTO'
    
    beak_obj_j = bpy.data.objects.new(f"Beakhead_Beam_{j}", curve_data)
    bpy.context.collection.objects.link(beak_obj_j)
    
    curve_data.bevel_mode = 'OBJECT'
    curve_data.bevel_object = bpy.data.objects["Beak_Profile"]
    curve_data.use_fill_caps = True
    
    if "Keel_Material" in bpy.data.materials:
        beak_obj_j.data.materials.append(bpy.data.materials["Keel_Material"])

# 4. Side Rails (Galjoensregels)
def create_rail(name, points, p_size):
    c_data = bpy.data.curves.new(name + "_Path", type='CURVE')
    c_data.dimensions = '3D'
    s_spline = c_data.splines.new('BEZIER')
    s_spline.bezier_points.add(len(points) - 1)
    for i, p in enumerate(points):
        s_spline.bezier_points[i].co = p
        s_spline.bezier_points[i].handle_left_type = 'AUTO'
        s_spline.bezier_points[i].handle_right_type = 'AUTO'
    r_obj = bpy.data.objects.new(name, c_data)
    bpy.context.collection.objects.link(r_obj)
    c_data.fill_mode = 'FULL'
    c_data.bevel_depth = p_size
    if "Keel_Material" in bpy.data.materials:
        r_obj.data.materials.append(bpy.data.materials["Keel_Material"])
    return r_obj

# Adding 3 rails on each side, aligned with the stacked beams
for side in [1, -1]:
    s_name = "R" if side == 1 else "L"
    for j in range(3):
        z_off = j * 0.76
        r_points = [
            (24.5, side * 0.6, 9.0 + z_off),
            (28.0, side * 0.5, 13.0 + z_off),
            (33.0, side * 0.2, 18.5 + z_off)
        ]
        create_rail(f"Beakhead_Rail_{s_name}_{j}", r_points, 0.1)

# 5. Spacers/Blocks between Rails
# Placing blocks that fit between the side rails and the central beams
for j in range(2): # Blocks between the 3 layers
    z_off_mid = j * 0.76 + 0.38
    for i in range(4):
        t = i / 3.0
        x = 25.5 + i * 2.2
        z = 10.0 + i * 2.2 + z_off_mid
        y_width = 1.0 - t * 0.4
        bpy.ops.mesh.primitive_cube_add(location=(x, 0, z))
        block = bpy.context.active_object
        block.name = f"Beakhead_Block_{j}_{i}"
        block.scale = (0.4, y_width, 0.3)
        bpy.ops.object.transform_apply(scale=True)
        if "Keel_Material" in bpy.data.materials:
            block.data.materials.append(bpy.data.materials["Keel_Material"])

print("Created multi-beam Beakhead structure with stacked timbers.")
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
    create_beakhead()
