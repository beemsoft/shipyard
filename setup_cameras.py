import socket
import json
import math

def setup_cameras():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import math

def ensure_camera(name):
    cam = bpy.data.objects.get(name)
    if not cam:
        cam_data = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, cam_data)
        bpy.context.collection.objects.link(cam)
    return cam

def set_camera_look_at(cam_obj, target_loc):
    # Remove existing Track To constraints
    for constraint in cam_obj.constraints:
        if constraint.type == 'TRACK_TO':
            cam_obj.constraints.remove(constraint)
    
    # Create a temporary empty for the target if it doesn't exist
    target_name = f"Target_{cam_obj.name}"
    target_obj = bpy.data.objects.get(target_name)
    if not target_obj:
        target_obj = bpy.data.objects.new(target_name, None)
        bpy.context.collection.objects.link(target_obj)
    
    target_obj.location = target_loc
    
    # Add Track To constraint
    ttc = cam_obj.constraints.new(type='TRACK_TO')
    ttc.target = target_obj
    ttc.track_axis = 'TRACK_NEGATIVE_Z'
    ttc.up_axis = 'UP_Y'

# Ship Dimensions (from get_ship_bbox.py):
# X from -21.1 to 25.8 (length ~47), Y from -9.6 to 9.6 (width ~19), Z from -0.2 to 44.0 (height ~44)

# 1. Side_Camera (Full ship view)
side_target = [2.3, 0.0, 20.0]
side_loc = [2.3, -100.0, 20.0] # Increased distance from -75 to -100 to ensure full height/length fit
side_cam = ensure_camera("Side_Camera")
side_cam.location = side_loc
set_camera_look_at(side_cam, side_target)
side_cam.data.lens = 35
side_cam.data.clip_start = 0.1
side_cam.data.clip_end = 2000.0

# 2. Camera_Back (Stern focus)
back_target = [-19.5, 0.0, 22.0] # Increased Z from 15 to 22
back_loc = [-100.0, -70.0, 45.0] # Moved further back and higher to capture more top/bottom
back_cam = ensure_camera("Camera_Back")
back_cam.location = back_loc
set_camera_look_at(back_cam, back_target)
back_cam.data.lens = 35 # Slightly more zoomed in for better stern focus
back_cam.data.clip_start = 0.1
back_cam.data.clip_end = 2000.0

# 3. Camera (Bow focus)
bow_target = [20.0, 0.0, 22.0] # Increased Z from 15 to 22
bow_loc = [80.0, -55.0, 35.0] # Moved slightly further and higher
bow_cam = ensure_camera("Camera")
bow_cam.location = bow_loc
set_camera_look_at(bow_cam, bow_target)
bow_cam.data.lens = 35 # Slightly more zoomed in for better bow focus
bow_cam.data.clip_start = 0.1
bow_cam.data.clip_end = 2000.0

print("All cameras (Side, Back, Bow) updated with TRACK_TO constraints and wider framing.")
"""

    payload = {
        "type": "execute_code",
        "params": {"code": code}
    }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(json.dumps(payload).encode('utf-8'))
            response = s.recv(1024 * 64)
            print(f"Blender response: {response.decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    setup_cameras()
