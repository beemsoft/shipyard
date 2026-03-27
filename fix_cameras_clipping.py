import socket
import json
import math

def fix_cameras():
    host = '127.0.0.1'
    port = 9876

    # New plan:
    # 1. Side Camera: Y = -110 is fine, but clipping is 100. Set clipping to 500.
    # 2. Back Camera: Currently at X=-90. Ship is from -20.6 to 33.4. Center is 6.4.
    # Distance from -90 to 33.4 is 123.4m.
    # To see 54m (height/width equivalent) from 123.4m with 50mm lens:
    # 50mm lens has approx 40 deg field of view.
    # At 123.4m, the view width is approx 2 * 123.4 * tan(20) = 2 * 123.4 * 0.36 = 88.8m.
    # So 54m *should* fit. Maybe it's not centered well or the ship is rotated?
    # Wait, the back camera rotation is (90, 0, -90). This looks at +X.
    # Let's move it to X=-110 to be safe and set clipping.

    code = """
import bpy
import mathutils
import math

# Bounding Box: {"min": [-20.6, -7.1, -0.2], "max": [33.4, 7.1, 44.0]}
# Center (approx): X: 6.4, Y: 0, Z: 21.9
center_x, center_y, center_z = 6.4, 0, 22.0

def update_camera(name, location, rotation_euler, clip_end=1000.0):
    if name in bpy.data.objects:
        cam_obj = bpy.data.objects[name]
        cam_obj.location = location
        cam_obj.rotation_euler = rotation_euler
        cam_obj.data.clip_end = clip_end
        print(f"Updated {name}: Loc={location}, Rot={rotation_euler}, Clip={clip_end}")
    else:
        # Create if not exists
        bpy.ops.object.camera_add(location=location, rotation=rotation_euler)
        cam_obj = bpy.context.active_object
        cam_obj.name = name
        cam_obj.data.clip_end = clip_end
        print(f"Created {name}")

# 1. Side Camera
update_camera("Camera", (center_x, -120.0, center_z), (math.radians(90), 0, 0))

# 2. Back Camera
update_camera("Camera_Back", (-110.0, 0.0, center_z), (math.radians(90), 0, math.radians(-90)))

# 3. User Perspective
# Point towards center (6.4, 0, 22)
user_cam_loc = (90.0, -90.0, 60.0)
target = mathutils.Vector((center_x, center_y, center_z))
loc = mathutils.Vector(user_cam_loc)
direction = target - loc
user_cam_rot_euler = direction.to_track_quat('-Z', 'Y').to_euler()
update_camera("User_Perspective_Camera_Full", user_cam_loc, user_cam_rot_euler)
"""
    try:
        with socket.create_connection((host, port), timeout=30) as s:
            command = {"type": "execute_code", "params": {"code": code}}
            s.sendall(json.dumps(command).encode('utf-8'))
            data = s.recv(16384)
            if data:
                print(json.loads(data.decode('utf-8'))["result"]["result"])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_cameras()
