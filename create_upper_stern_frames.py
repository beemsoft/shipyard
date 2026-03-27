import socket
import json

def create_upper_stern_frames():
    host = '127.0.0.1'
    port = 9876
    
    code = """
import bpy
import math

# Cleanup existing upper stern frames
for obj in bpy.data.objects:
    if "Upper_Stern_Frame" in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)

# Define 5 vertical frames that rise from the Wing Transom
# Wing Transom is at X=-18.95, Y from -4 to +4, Z=9.5
# These frames will curve slightly inward (tumblehome) and reach up to Z=15 or so.

def create_upper_frame(y_pos, name):
    # Points: Base on Wing Transom, Middle, Top
    points = [
        (-18.95, y_pos, 9.5),
        (-19.5, y_pos * 0.9, 12.0),
        (-19.2, y_pos * 0.8, 15.0)
    ]
    
    curve_data = bpy.data.curves.new(f"{name}_Path", type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    
    for i, p in enumerate(points):
        spline.bezier_points[i].co = p
        spline.bezier_points[i].handle_left_type = 'AUTO'
        spline.bezier_points[i].handle_right_type = 'AUTO'
        
    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    
    # Use standard profile
    if "Post_Profile" in bpy.data.objects:
        curve_data.bevel_mode = 'OBJECT'
        curve_data.bevel_object = bpy.data.objects["Post_Profile"]
    else:
        curve_data.bevel_depth = 0.15
        
    curve_data.use_fill_caps = True
    
    # Material
    mat = bpy.data.materials.get("Wood_Material")
    if mat:
        obj.data.materials.append(mat)

# Create 5 frames across the transom
y_positions = [-4.0, -2.0, 0.0, 2.0, 4.0]
for i, y in enumerate(y_positions):
    create_upper_frame(y, f"Upper_Stern_Frame_{i}")

print(f"Created {len(y_positions)} upper stern frames (vertical timbers).")
"""
    try:
        with socket.create_connection((host, port), timeout=5) as s:
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
    create_upper_stern_frames()
