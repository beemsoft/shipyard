import socket
import json

def create_fashion_pieces():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import math

# Cleanup existing fashion pieces
for obj in bpy.data.objects:
    if "Fashion_Piece" in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)

# Define the points for the Fashion Pieces (Fashion Timbers)
# They curve from the keel/sternpost junction up to the Wing Transom edges.
# Top of Wing Transom is at X=-18.95, Y=+/- 4.0, Z=9.5
# Bottom of Sternpost is at X=-18.95, Y=0, Z=0.4

def create_fashion_piece(side):
    points = [
        (-18.95, 0.0, 0.4), # Bottom at keel
        (-19.5, side * 2.0, 4.0), # Middle curve
        (-18.95, side * 4.0, 9.5) # Top at wing transom
    ]
    
    curve_data = bpy.data.curves.new(f"Fashion_Piece_{side}", type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    
    for i, p in enumerate(points):
        spline.bezier_points[i].co = p
        spline.bezier_points[i].handle_left_type = 'AUTO'
        spline.bezier_points[i].handle_right_type = 'AUTO'
        
    obj = bpy.data.objects.new(f"Fashion_Piece_{'R' if side > 0 else 'L'}", curve_data)
    bpy.context.collection.objects.link(obj)
    
    # Use standard profile if it exists
    if "Post_Profile" in bpy.data.objects:
        curve_data.bevel_mode = 'OBJECT'
        curve_data.bevel_object = bpy.data.objects["Post_Profile"]
    else:
        # Create a simple profile
        curve_data.bevel_depth = 0.2
        
    curve_data.use_fill_caps = True
    
    # Material
    mat = bpy.data.materials.get("Wood_Material")
    if mat:
        obj.data.materials.append(mat)

create_fashion_piece(1.0)
create_fashion_piece(-1.0)
print("Created Fashion Pieces (R and L) at the stern.")
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
    create_fashion_pieces()
