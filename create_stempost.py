import socket
import json

def create_stempost():
    host = '127.0.0.1'
    port = 9876

    # Keel length: 37.9m (along X-axis, centered at 0,0,0)
    # The front of the ship (bow) is at X = +18.95m.
    # The stempost curves forward and up.
    # It should follow the bow shape and extend further upward.

    try:
        with socket.create_connection((host, port), timeout=5) as s:
            code = """
import bpy
import mathutils

# 1. Stempost Parameters
# Starts at the front of the keel (X = 18.95, Z = 0.4)
x_start = 18.95
z_start = 0.4
thickness = 0.6
width = 0.6

# 2. Points for the stempost profile
# (X, Y, Z)
# The stempost curves forward and up from the keel.
points = [
    (18.95, 0.0, 0.4),    # Start at front of Keel
    (20.0, 0.0, 1.0),     # Curve up/forward
    (22.0, 0.0, 4.0),     # Sweeping up
    (23.5, 0.0, 8.0),     # Near upper deck level
    (24.5, 0.0, 12.0),    # Following the bow flare
    (25.5, 0.0, 15.0)     # Final top tip
]

# 3. Cleanup existing
if "Stempost" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Stempost"], do_unlink=True)
for mesh in bpy.data.meshes:
    if mesh.name.startswith("Stempost"):
        bpy.data.meshes.remove(mesh)
for curve in bpy.data.curves:
    if curve.name.startswith("Stempost"):
        bpy.data.curves.remove(curve)

# 4. Create Curve Path
curve_data = bpy.data.curves.new("Stempost_Path", type='CURVE')
curve_data.dimensions = '3D'
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(len(points) - 1)

for i, p in enumerate(points):
    spline.bezier_points[i].co = p
    spline.bezier_points[i].handle_left_type = 'AUTO'
    spline.bezier_points[i].handle_right_type = 'AUTO'

stem_obj = bpy.data.objects.new("Stempost", curve_data)
bpy.context.collection.objects.link(stem_obj)

# 5. Rectangular profile (using curve properties)
# For a rectangular cross-section, we can use a bevel object
if "Post_Profile" not in bpy.data.objects:
    profile_size = 0.6
    profile_curve = bpy.data.curves.new("Post_Profile", type='CURVE')
    profile_curve.dimensions = '2D'
    p_spline = profile_curve.splines.new('POLY')
    p_spline.use_cyclic_u = True
    p_spline.points.add(3)
    p_spline.points[0].co = (-profile_size/2, -profile_size/2, 0, 1)
    p_spline.points[1].co = (profile_size/2, -profile_size/2, 0, 1)
    p_spline.points[2].co = (profile_size/2, profile_size/2, 0, 1)
    p_spline.points[3].co = (-profile_size/2, profile_size/2, 0, 1)
    profile_obj = bpy.data.objects.new("Post_Profile", profile_curve)
    bpy.context.collection.objects.link(profile_obj)
    profile_obj.hide_viewport = True
    profile_obj.hide_render = True

curve_data.bevel_mode = 'OBJECT'
curve_data.bevel_object = bpy.data.objects["Post_Profile"]
curve_data.use_fill_caps = True

# 6. Apply Material
if "Keel_Material" in bpy.data.materials:
    mat = bpy.data.materials["Keel_Material"]
    stem_obj.data.materials.append(mat)

print(f"Created curved 'Stempost' starting at {points[0]}")
"""
            command = {
                "type": "execute_code",
                "params": {
                    "code": code
                }
            }

            s.sendall(json.dumps(command).encode('utf-8'))
            data = s.recv(16384)
            if data:
                response = json.loads(data.decode('utf-8'))
                print("Blender response:")
                print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_stempost()
