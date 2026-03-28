import socket
import json

def create_stern_upper_rails():
    host = '127.0.0.1'
    port = 9876
    
    code = """
import bpy
import math

# Cleanup existing upper rails
for obj in bpy.data.objects:
    if "Stern_Upper_Rail" in obj.name or "Taffrail" in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)

# Points from Upper_Stern_Frame:
# Base: (-18.95, y_pos, 9.5)
# Middle: (-18.95, y_pos * 0.9, 12.0)
# Top: (-18.95, y_pos * 0.8, 15.0)

y_positions = [-4.0, -2.0, 0.0, 2.0, 4.0]

def create_horizontal_rail(z_level, x_pos, y_scale, name):
    # This creates a curved rail across the vertical frames at a certain height
    points = []
    for y in y_positions:
        # Aligned to flat vertical transom at X=-18.95
        if z_level == 12.0:
            points.append((-18.95, y * 0.9, 12.0))
        elif z_level == 15.0:
            points.append((-18.95, y * 0.8, 15.0))
        elif z_level == 13.5: # Intermediate level
            points.append((-18.95, y * 0.85, 13.5))

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
    
    # Use Post_Profile
    if "Post_Profile" in bpy.data.objects:
        curve_data.bevel_mode = 'OBJECT'
        curve_data.bevel_object = bpy.data.objects["Post_Profile"]
    else:
        curve_data.bevel_depth = 0.1
        
    curve_data.use_fill_caps = True
    
    # Material
    mat = bpy.data.materials.get("Wood_Material")
    if mat:
        obj.data.materials.append(mat)

# 1. Gallery Rail (Middle)
create_horizontal_rail(12.0, -19.5, 0.9, "Stern_Upper_Rail_Gallery")

# 2. Taffrail Base (Top of frames)
create_horizontal_rail(15.0, -19.2, 0.8, "Stern_Upper_Rail_Taffrail_Base")

# 3. Create the Taffrail Arch (The crown of the stern)
def create_taffrail_arch():
    # An arch above the top rail, aligned to X=-18.95
    points = [
        (-18.95, -3.2, 15.0),
        (-18.95, -2.0, 16.5),
        (-18.95, 0.0, 17.5),
        (-18.95, 2.0, 16.5),
        (-18.95, 3.2, 15.0)
    ]
    
    curve_data = bpy.data.curves.new("Taffrail_Arch_Path", type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    
    for i, p in enumerate(points):
        spline.bezier_points[i].co = p
        spline.bezier_points[i].handle_left_type = 'AUTO'
        spline.bezier_points[i].handle_right_type = 'AUTO'
        
    obj = bpy.data.objects.new("Taffrail_Arch", curve_data)
    bpy.context.collection.objects.link(obj)
    
    # Make it thicker/decorative
    curve_data.bevel_depth = 0.2
    curve_data.use_fill_caps = True
    
    mat = bpy.data.materials.get("Wood_Material")
    if mat:
        obj.data.materials.append(mat)

create_taffrail_arch()

# 4. Add "Wulpaard" (Upper Transom Planking area) - simplified as a plane or box
# For frame-building mode, we might just add another rail or two to define the surface.
create_horizontal_rail(13.5, -19.4, 0.85, "Stern_Upper_Rail_Middle")

print("Created upper rails and taffrail arch at the stern.")
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
    create_stern_upper_rails()
