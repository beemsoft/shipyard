import socket
import json
import math

# Target the stern center
target_location = [-18.95, 0.0, 7.5]
camera_location = [-45.0, -35.0, 15.0]

# Calculate rotation to look at target
dx = target_location[0] - camera_location[0]
dy = target_location[1] - camera_location[1]
dz = target_location[2] - camera_location[2]

dist_xy = math.sqrt(dx**2 + dy**2)
rot_x_blender = math.pi/2 - math.atan2(dz, dist_xy)
rot_z_blender = math.atan2(dy, dx) - math.pi/2

blender_code = f"""
import bpy
import math

cam = bpy.data.objects.get('Camera_Back')
if not cam:
    cam_data = bpy.data.cameras.new('Camera_Back')
    cam = bpy.data.objects.new('Camera_Back', cam_data)
    bpy.context.collection.objects.link(cam)

cam.location = ({camera_location[0]}, {camera_location[1]}, {camera_location[2]})
cam.rotation_euler = ({rot_x_blender}, 0.0, {rot_z_blender})
cam.data.lens = 35
cam.data.clip_start = 0.1
cam.data.clip_end = 1000.0

print(f"Repositioned Camera_Back to {{cam.location}} with rotation {{cam.rotation_euler}}")
"""

def execute_blender_code(code):
    host = '127.0.0.1'
    port = 9876
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
                return json.loads(data.decode('utf-8'))
    except Exception as e:
        return {"status": "error", "message": str(e)}

response = execute_blender_code(blender_code)
print(json.dumps(response, indent=2))
