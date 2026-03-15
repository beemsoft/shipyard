import socket
import json

def reposition_cameras():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import mathutils
import math

def look_at(obj, target):
    if not isinstance(target, mathutils.Vector):
        target = mathutils.Vector(target)
    
    loc = obj.location
    direction = target - loc
    # Camera looks along -Z, Up is Y
    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj.rotation_euler = rot_quat.to_euler()

def set_camera(name, pos, target):
    if name not in bpy.data.objects:
        cam_data = bpy.data.cameras.new(name)
        cam_obj = bpy.data.objects.new(name, cam_data)
        bpy.context.collection.objects.link(cam_obj)
    else:
        cam_obj = bpy.data.objects[name]
    
    cam_obj.location = pos
    look_at(cam_obj, target)
    print(f"Set {name} to {pos}, looking at {target}")

# Ship dimensions: Keel ~38m, max height ~20m.
# Center of the ship is roughly at X=0, Y=0, Z=5 (mid-hull height)
center = (0, 0, 5)

# 1. 'Camera' - Side View (Starboard)
# Should be far enough to see the whole 38m length.
# Field of view at distance D: width = 2 * D * tan(fov/2)
# For 50mm lens (default), horizontal FOV is ~39.6 degrees.
# tan(20 deg) ~ 0.36. 2 * 0.36 = 0.72. 
# To see 40m, D * 0.72 = 40 => D = 55.5m.
# Increased to 80m to ensure everything is in view.
set_camera("Camera", (0, -80, 10), center)

# 2. 'Camera_Back' - Stern View
# Looking from behind (negative X).
# Ship width is ~12m, but height is ~20m.
# Increased distance to 80m as well.
set_camera("Camera_Back", (-80, 0, 15), center)

# 3. 'User_Perspective_Camera_Full' - 3/4 Perspective View
# Front-side-above. Increased distance a bit more.
set_camera("User_Perspective_Camera_Full", (55, -55, 30), center)

print("Repositioned cameras successfully.")
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
    reposition_cameras()
