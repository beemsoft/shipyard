import socket
import json

def create_sternpost():
    host = '127.0.0.1'
    port = 9876
    
    # Keel parameters
    keel_length = 37.9
    keel_height = 0.8
    keel_width = 0.6
    
    # Sternpost parameters
    # The sternpost goes upwards at an angle. 
    # Let's make it about 10 meters high for now as a base.
    # It should be attached at the back of the keel (X = -18.95).
    sternpost_height = 8.0
    sternpost_thickness = 0.6
    sternpost_width = 0.6
    # Angle (rake): Dutch ships often had a slightly raked sternpost. 
    # Let's tilt it back by about 10-15 degrees (approx 0.2 radians).
    rake_angle = 0.2 

    try:
        with socket.create_connection((host, port), timeout=5) as s:
            code = f"""
import bpy
import math

# 1. Sternpost dimensions
height = {sternpost_height}
thickness = {sternpost_thickness}
width = {sternpost_width}
rake = {rake_angle}

# Position at the back of the keel
# Keel is centered at (0,0,0) with length 37.9, so back is at X = -18.95
# We want the bottom of the sternpost to meet the top of the keel at the back end.
# Keel top is at Z = 0.4 (half of 0.8)
start_x = -18.95
start_z = 0.4

if "Sternpost" in bpy.data.objects:
    sternpost = bpy.data.objects["Sternpost"]
    print("Found existing 'Sternpost', updating")
else:
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    sternpost = bpy.context.active_object
    sternpost.name = "Sternpost"
    print("Created new 'Sternpost'")

# Set dimensions: X is thickness, Y is width, Z is height
# We'll use scale and apply it
sternpost.scale = (thickness / 2.0, width / 2.0, height / 2.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Rotate it (rake) - rotate around Y axis
sternpost.rotation_euler = (0, -rake, 0)

# Position it
# To make the bottom-center of the beam sit at (start_x, 0, start_z):
# The beam's center is at (0,0,0) in local space.
# After rotation, we need to offset it.
# Simple way: move the origin to the bottom of the mesh first.
bpy.context.view_layer.objects.active = sternpost
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
# Move mesh up so bottom is at 0
bpy.ops.transform.translate(value=(0, 0, height/2.0))
bpy.ops.object.mode_set(mode='OBJECT')

# Now set location
sternpost.location = (start_x, 0, start_z)

# Apply material (same as Keel)
if "Keel_Material" in bpy.data.materials:
    mat = bpy.data.materials["Keel_Material"]
    if not sternpost.data.materials:
        sternpost.data.materials.append(mat)
    else:
        sternpost.data.materials[0] = mat

print(f"'Sternpost' added at {{sternpost.location}}")
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
    create_sternpost()
