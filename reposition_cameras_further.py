import socket
import json
import math

def reposition_cameras_further():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import mathutils
import math

# Bounding Box: {"min": [-20.6, -7.1, -0.2], "max": [33.4, 7.1, 44.0]}
# Ship Center (approx): X: 6.4, Y: 0, Z: 21.9
# Length (X): 54.0m
# Width (Y): 14.2m
# Height (Z): 44.2m

# Move cameras further away to provide more "breathing room" in the snapshots.
# Previous side Y was -90, now -110.
# Previous back X was -70, now -90.
# Previous user cam was at (70, -70, 50), now (90, -90, 60).

side_cam_loc = (6.4, -110.0, 22.0)
side_cam_rot = (math.radians(90), 0, 0)

back_cam_loc = (-90.0, 0.0, 22.0)
back_cam_rot = (math.radians(90), 0, math.radians(-90))

user_cam_loc = (90.0, -90.0, 60.0)
target = mathutils.Vector((6.4, 0.0, 22.0))
loc = mathutils.Vector(user_cam_loc)
direction = target - loc
user_cam_rot_euler = direction.to_track_quat('-Z', 'Y').to_euler()

def update_camera(name, location, rotation):
    if name in bpy.data.objects:
        cam = bpy.data.objects[name]
        cam.location = location
        cam.rotation_euler = rotation
        print(f"Updated {name} to {location}")
    else:
        bpy.ops.object.camera_add(location=location, rotation=rotation)
        cam = bpy.context.active_object
        cam.name = name
        print(f"Created {name}")

update_camera("Camera", side_cam_loc, side_cam_rot)
update_camera("Camera_Back", back_cam_loc, back_cam_rot)
update_camera("User_Perspective_Camera_Full", user_cam_loc, user_cam_rot_euler)
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
                response = json.loads(data.decode('utf-8'))
                print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reposition_cameras_further()
