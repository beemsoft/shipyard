import socket
import json

def create_beakhead_lower_beam():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import mathutils
import math

# 1. Cleanup
for obj in bpy.data.objects:
    if obj.name.startswith("Beakhead_Lower_Beam"):
        bpy.data.objects.remove(obj, do_unlink=True)
for mesh in bpy.data.meshes:
    if mesh.name.startswith("Beakhead_Lower_Beam"):
        bpy.data.meshes.remove(mesh)
for curve in bpy.data.curves:
    if curve.name.startswith("Beakhead_Lower_Beam"):
        bpy.data.curves.remove(curve)

# 2. Parameters
# Starting lower on the stempost curve
# The stempost has points at:
# (18.95, 0.0, 0.4)
# (19.95, 0.0, 0.9)
# (21.95, 0.0, 4.4)
# (23.45, 0.0, 7.9)
# (24.95, 0.0, 9.4)
# (26.95, 0.0, 10.4)
# (29.95, 0.0, 11.9)
# (31.95, 0.0, 13.4)

# We'll create a massive "knee of the head" (solid white part in the model image)
# This fills the space between the stempost and the keel/waterline.

points = [
    (18.95, 0.0, 0.4),    # Start at keel
    (22.0, 0.0, 1.0),
    (24.0, 0.0, 3.0),
    (26.0, 0.0, 6.0),
    (28.0, 0.0, 8.5),     # Adjusting to sit under beak beam
    (30.0, 0.0, 11.0),
    (32.0, 0.0, 14.0),
    (34.0, 0.0, 17.0)
]

# 3. Create Curve Path
curve_data = bpy.data.curves.new("Beakhead_Lower_Beam_Path", type='CURVE')
curve_data.dimensions = '3D'
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(len(points) - 1)

for i, p in enumerate(points):
    spline.bezier_points[i].co = p
    spline.bezier_points[i].handle_left_type = 'AUTO'
    spline.bezier_points[i].handle_right_type = 'AUTO'

beam_obj = bpy.data.objects.new("Beakhead_Lower_Beam", curve_data)
bpy.context.collection.objects.link(beam_obj)

# 4. Rectangular profile - making it wider to look like a solid bulkhead/knee
if "Post_Profile" not in bpy.data.objects:
    # Create a wider profile for the knee
    profile_size_x = 0.6
    profile_size_y = 1.2 # Wide to look massive
    profile_curve = bpy.data.curves.new("Knee_Profile", type='CURVE')
    profile_curve.dimensions = '2D'
    p_spline = profile_curve.splines.new('POLY')
    p_spline.use_cyclic_u = True
    p_spline.points.add(3)
    p_spline.points[0].co = (-profile_size_x/2, -profile_size_y/2, 0, 1)
    p_spline.points[1].co = (profile_size_x/2, -profile_size_y/2, 0, 1)
    p_spline.points[2].co = (profile_size_x/2, profile_size_y/2, 0, 1)
    p_spline.points[3].co = (-profile_size_x/2, profile_size_y/2, 0, 1)
    profile_obj = bpy.data.objects.new("Knee_Profile", profile_curve)
    bpy.context.collection.objects.link(profile_obj)
    profile_obj.hide_viewport = True

curve_data.bevel_mode = 'OBJECT'
curve_data.bevel_object = bpy.data.objects.get("Knee_Profile") or bpy.data.objects.get("Post_Profile")
curve_data.use_fill_caps = True

# 5. Apply Material
if "Keel_Material" in bpy.data.materials:
    mat = bpy.data.materials["Keel_Material"]
    beam_obj.data.materials.append(mat)

print("Created lower beam below the beakhead to smooth the bow curve.")
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
    create_beakhead_lower_beam()
