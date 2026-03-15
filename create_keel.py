import socket
import json

def create_keel_shape():
    host = '127.0.0.1'
    port = 9876
    
    # Accurate dimensions for the keel based on historical data for 'De Zeven Provinciën':
    # Length on gundeck is 163 Amsterdam feet (approx. 46m).
    # Keel length is 134 Amsterdam feet (approx. 37.9m).
    length = 37.9
    width = 0.6
    height = 0.8
    
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            # Code to delete the 'Cube' and add a 'Keel' (a long box)
            code = f"""
import bpy
import bmesh

# 1. Remove the 'Cube' if it exists
if "Cube" in bpy.data.objects:
    cube = bpy.data.objects["Cube"]
    bpy.data.objects.remove(cube, do_unlink=True)
    print("Deleted 'Cube'")
else:
    print("'Cube' not found")

# 2. Create the Keel
# De Zeven Provincien was approx 163 Amsterdam feet (46m) long (gundeck).
# The actual keel length is 134 Amsterdam feet (37.9m).
# We'll create a long, narrow box to represent the keel.

length = {length}
width = {width}
height = {height}

# 3. Handle object creation/update
if "Keel" in bpy.data.objects:
    keel = bpy.data.objects["Keel"]
    print("Found existing 'Keel', resetting and updating dimensions")
    # To be safe, we'll replace it with a fresh cube of known 2x2x2 size
    loc = (0, 0, 0)
    bpy.data.objects.remove(keel, do_unlink=True)
    bpy.ops.mesh.primitive_cube_add(location=loc)
    keel = bpy.context.active_object
    keel.name = "Keel"
else:
    # Add a cube and scale it to be a keel
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    keel = bpy.context.active_object
    keel.name = "Keel"
    print("Created new 'Keel' at (0, 0, 0)")

# Scale it: x is length, y is width, z is height
# primitive_cube_add creates a 2x2x2 cube, so scale factors are half of desired dimensions
keel.scale = (length / 2.0, width / 2.0, height / 2.0)

# Apply scale to make it 'real' geometry
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add a simple material
if "Keel_Material" not in bpy.data.materials:
    mat = bpy.data.materials.new(name="Keel_Material")
    mat.diffuse_color = (0.1, 0.05, 0.0, 1.0) # Dark wood color
else:
    mat = bpy.data.materials["Keel_Material"]

if not keel.data.materials:
    keel.data.materials.append(mat)
else:
    keel.data.materials[0] = mat

print("Created 'Keel' at (0, 0, 0)")
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
