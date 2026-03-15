import socket
import json

def rotate_cameras_to_model():
    host = '127.0.0.1'
    port = 9876
    
    # We will aim at the center of the keel at some height (to capture the whole structure)
    # The Keel is 37.9m long. Stem/Stern posts are 8m and 10m high.
    # Target (0, 0, 4.5) to look at the center of the vertical components.
    
    code = """
import bpy
import mathutils

def point_camera_at_target(camera_name, target_location):
    if camera_name in bpy.data.objects:
        cam = bpy.data.objects[camera_name]
        target = mathutils.Vector(target_location)
        
        # Calculate direction from camera to target
        direction = target - cam.location
        # Point the camera's -Z axis (forward) towards the target, and +Y axis (up) towards the world +Z
        rot_quat = direction.to_track_quat('-Z', 'Y')
        
        # Set camera rotation
        cam.rotation_euler = rot_quat.to_euler()
        print(f"Rotated '{camera_name}' towards {target_location}. New rotation: {cam.rotation_euler}")
    else:
        print(f"Camera '{camera_name}' not found")

target_loc = (0.0, 0.0, 4.5)
point_camera_at_target("Camera", target_loc)
point_camera_at_target("Camera_Back", target_loc)
"""
    command = {
        "type": "execute_code",
        "params": {
            "code": code
        }
    }
    
    try:
        with socket.create_connection((host, port), timeout=30) as s:
            s.sendall(json.dumps(command).encode('utf-8'))
            data = s.recv(16384)
            if data:
                response = json.loads(data.decode('utf-8'))
                print("Blender response:")
                print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    rotate_cameras_to_model()
