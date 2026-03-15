import socket
import json

def switch_to_side_view():
    host = '127.0.0.1'
    port = 9876
    
    code = """
import bpy

# 1. Get the side camera
cam = bpy.data.objects.get("Camera")

if cam:
    # 2. Set it as the active camera for the scene
    bpy.context.scene.camera = cam
    
    # 3. Find 3D View areas and set them to camera view
    found_view = False
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.region_3d.view_perspective = 'CAMERA'
                    found_view = True
    
    if found_view:
        print("Successfully switched 3D View to 'Camera' (side) view.")
    else:
        print("Set active camera to 'Camera', but no 3D View area was found to update.")
else:
    print("Error: 'Camera' object not found in the scene.")
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
    switch_to_side_view()
