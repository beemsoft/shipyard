import socket
import json

def capture_viewport_full():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import mathutils

def get_viewport_view():
    # Find the first 3D View area
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    rv3d = space.region_3d
                    return rv3d
    return None

rv3d = get_viewport_view()
if rv3d:
    # Use User_Perspective_Camera_Full as the name
    cam_name = "User_Perspective_Camera_Full"
    
    if cam_name in bpy.data.objects:
        cam_obj = bpy.data.objects[cam_name]
    else:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        bpy.context.collection.objects.link(cam_obj)
    
    # Set location and rotation from viewport
    # The matrix_world of the region_3d is the inverse of the view matrix
    view_matrix = rv3d.view_matrix
    inv_view_matrix = view_matrix.inverted()
    
    cam_obj.matrix_world = inv_view_matrix
    
    # Shift backwards along the local Z-axis
    # Backward in Blender camera is +Z (because default view is -Z)
    shift_amount = 35.0 # Balanced view distance
    direction = cam_obj.matrix_world.to_quaternion() @ mathutils.Vector((0.0, 0.0, 1.0))
    cam_obj.location += direction * shift_amount
    
    # Adjust camera properties
    cam_obj.data.lens = 50 # Default lens
    
    # Output success
    print(f"SUCCESS: Created/Updated '{cam_name}' from viewport (shifted backwards).")
    print(f"Location: {list(cam_obj.location)}")
    print(f"Rotation: {list(cam_obj.rotation_euler)}")
else:
    print("ERROR: Could not find a 3D Viewport to capture from.")
"""

    try:
        with socket.create_connection((host, port), timeout=5) as s:
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
    capture_viewport_full()
