import socket
import json

def create_stern_galleries():
    host = '127.0.0.1'
    port = 9876
    
    code = """
import bpy
import math

# Cleanup existing gallery pieces
for obj in bpy.data.objects:
    if "Stern_Gallery" in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)

# Gallery pieces connect the fashion pieces to the upper stern frames.
# Fashion Piece top: (-18.95, side * 4.0, 9.5)
# Upper Frame Base: (-18.95, side * 4.0, 9.5)
# Let's add side gallery frames (the 'balcony' area)

def create_gallery_side(side):
    # Curve from the side of the hull to the transom
    # Roughly at Z=10 to Z=14
    
    # 1. Lower gallery rail
    points_lower = [
        (-15.0, side * 6.0, 9.0),  # On the hull side
        (-17.0, side * 5.5, 9.2),
        (-18.95, side * 4.0, 9.5)  # Meeting the wing transom/fashion piece
    ]
    
    # 2. Upper gallery rail
    points_upper = [
        (-15.0, side * 5.5, 12.0),
        (-17.0, side * 5.0, 12.0),
        (-19.5, side * 3.6, 12.0) # Meeting the upper stern frame at Z=12 (4 * 0.9)
    ]
    
    def create_curve(points, name):
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
        curve_data.bevel_depth = 0.1
        curve_data.use_fill_caps = True
        mat = bpy.data.materials.get("Wood_Material")
        if mat:
            obj.data.materials.append(mat)
            
    create_curve(points_lower, f"Stern_Gallery_Lower_{'R' if side > 0 else 'L'}")
    create_curve(points_upper, f"Stern_Gallery_Upper_{'R' if side > 0 else 'L'}")

create_gallery_side(1.0)
create_gallery_side(-1.0)

print("Created stern gallery side frames.")
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
    create_stern_galleries()
