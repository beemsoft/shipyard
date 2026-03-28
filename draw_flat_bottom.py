import socket
import json

def draw_flat_bottom():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import math

def create_flat_bottom(name, x_start, x_end, width, material_name):
    # The 7 Provinces has a flat bottom. 
    # We'll represent it as a set of transverse beams or a single plane.
    # Usually, the floor timbers are flat.
    
    # Let's create a series of transverse beams to represent the flat floor.
    # Or better, a NURBS surface or a mesh.
    # The user says "draw that first", starting from the bottom.
    
    # Dimensions
    # width is total width at the floor.
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Vertices for a simple rectangular flat bottom
    # Located just above the keel (keel top Z is approx 0.6 to 0.75)
    z = 0.7
    half_w = width / 2.0
    
    verts = [
        (x_start, -half_w, z), (x_end, -half_w, z),
        (x_end, half_w, z), (x_start, half_w, z)
    ]
    faces = [(0, 1, 2, 3)]
    
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    if material_name in bpy.data.materials:
        obj.data.materials.append(bpy.data.materials[material_name])
        
    return obj

# Parameters for the flat bottom of the 7 Provinces
# Keel is from -18.95 to 18.95 approx (length 37.9)
# The flat floor is usually in the midsection, narrowing towards ends.
# But "starting from the bottom, the 7 provinces has a flat bottom" 
# might imply the whole bottom is relatively flat.

# Let's create it.
x_start = -15.0
x_end = 15.0
width = 8.0 # Approx 8 meters wide floor

# Clean up existing flat bottom if any
if "Flat_Bottom" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Flat_Bottom"], do_unlink=True)

fb = create_flat_bottom("Flat_Bottom", x_start, x_end, width, "Rib_Material")
print(f"Created flat bottom from {x_start} to {x_end} with width {width}")
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
    draw_flat_bottom()
