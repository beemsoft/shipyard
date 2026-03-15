import socket
import json

def create_keel_shape():
    host = '127.0.0.1'
    port = 9876
    
    # Accurate dimensions for the keel based on historical data for 'De Zeven Provinciën':
    length = 37.9
    width = 0.6
    height = 0.8
    
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            code = f"""
import bpy
import mathutils

# 1. Keel Parameters
length = {length}
width = {width}
height = {height}

# Points for a slightly curved keel (dipped in middle)
points = [
    (-length/2, 0.0, 0.4),
    (0.0, 0.0, 0.2),
    (length/2, 0.0, 0.4)
]

# 2. Cleanup existing
if "Keel" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Keel"], do_unlink=True)
for curve in bpy.data.curves:
    if curve.name.startswith("Keel"):
        bpy.data.curves.remove(curve)

# 3. Create Curve Path
curve_data = bpy.data.curves.new("Keel_Path", type='CURVE')
curve_data.dimensions = '3D'
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(len(points) - 1)

for i, p in enumerate(points):
    spline.bezier_points[i].co = p
    spline.bezier_points[i].handle_left_type = 'AUTO'
    spline.bezier_points[i].handle_right_type = 'AUTO'

keel_obj = bpy.data.objects.new("Keel", curve_data)
bpy.context.collection.objects.link(keel_obj)

# 4. Profile for the Keel (0.6 wide, 0.8 high)
if "Keel_Profile" not in bpy.data.objects:
    p_width = {width}
    p_height = {height}
    profile_curve = bpy.data.curves.new("Keel_Profile", type='CURVE')
    profile_curve.dimensions = '2D'
    p_spline = profile_curve.splines.new('POLY')
    p_spline.use_cyclic_u = True
    p_spline.points.add(3)
    p_spline.points[0].co = (-p_width/2, -p_height/2, 0, 1)
    p_spline.points[1].co = (p_width/2, -p_height/2, 0, 1)
    p_spline.points[2].co = (p_width/2, p_height/2, 0, 1)
    p_spline.points[3].co = (-p_width/2, p_height/2, 0, 1)
    profile_obj = bpy.data.objects.new("Keel_Profile", profile_curve)
    bpy.context.collection.objects.link(profile_obj)
    profile_obj.hide_viewport = True
    profile_obj.hide_render = True

curve_data.bevel_mode = 'OBJECT'
curve_data.bevel_object = bpy.data.objects["Keel_Profile"]
curve_data.use_fill_caps = True

# 5. Apply Material
if "Keel_Material" not in bpy.data.materials:
    mat = bpy.data.materials.new(name="Keel_Material")
    mat.diffuse_color = (0.1, 0.05, 0.0, 1.0)
else:
    mat = bpy.data.materials["Keel_Material"]
keel_obj.data.materials.append(mat)

print("Created curved 'Keel'")
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
    create_keel_shape()
