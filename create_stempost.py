import socket
import json

def create_stempost():
    host = '127.0.0.1'
    port = 9876

    # Keel length: 37.9m (along X-axis, centered at 0,0,0)
    # The front of the ship (bow) is at X = +18.95m.
    # The stempost is usually raked forward.

    try:
        with socket.create_connection((host, port), timeout=5) as s:
            code = """
import bpy
import math

# 1. Stempost Parameters
# Located at the front of the keel (X = 18.95)
x_pos = 18.95
height = 10.0
thickness = 0.6
width = 0.6
rake_angle = 0.3 # Radians (~17.2 degrees forward)

# 2. Create the Stempost (a cube scaled into a beam)
if "Stempost" in bpy.data.objects:
    stempost = bpy.data.objects["Stempost"]
    bpy.data.objects.remove(stempost, do_unlink=True)
    print("Deleted existing 'Stempost'")

bpy.ops.mesh.primitive_cube_add(location=(x_pos, 0, 0))
stempost = bpy.context.active_object
stempost.name = "Stempost"

# 3. Scaling
# primitive_cube_add creates a 2x2x2 cube
stempost.scale = (thickness / 2.0, width / 2.0, height / 2.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# 4. Positioning and Rotation
# We want the bottom of the beam to be on top of the keel (Z = 0.4)
# And the beam should rake forward.
# To rake forward (away from the center), we rotate around the Y axis.
# Since it's at +X, a positive rotation around Y tilts it towards +X (forward).
stempost.rotation_euler[1] = rake_angle

# After rotation, we need to adjust the location so the bottom is at the front of the keel.
# The beam's center is at (x_pos, 0, height/2). 
# We'll adjust it so the bottom face (in its local space) sits at X=18.95, Z=0.4.
# A simpler way: set the origin to the bottom face.
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
# Move everything up by half its height in local Z
bpy.ops.transform.translate(value=(0, 0, height/2.0))
bpy.ops.object.mode_set(mode='OBJECT')

# Now the origin is at the bottom face. 
# Set position to top of keel (Z=0.4) at the front (X=18.95)
stempost.location = (x_pos, 0, 0.4)

# 5. Apply Material
if "Keel_Material" in bpy.data.materials:
    mat = bpy.data.materials["Keel_Material"]
    if not stempost.data.materials:
        stempost.data.materials.append(mat)
    else:
        stempost.data.materials[0] = mat

print(f"Created 'Stempost' at {stempost.location} with rake angle {rake_angle}")
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
