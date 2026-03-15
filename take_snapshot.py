import socket
import json
import os
from datetime import datetime

def take_snapshot():
    host = '127.0.0.1'
    port = 9876

    # Current date and time for labeling
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    # Folder to store the snapshots
    base_dir = "C:/Users/hpbee/IdeaProjects/Blender/shipyard/1666/7-provinces/images"

    # We will take three snapshots: side (main camera), back, and the full model user perspective camera.
    cameras = [
        ("Camera", "side"),
        ("Camera_Back", "back"),
        ("User_Perspective_Camera_Full", "user_perspective")
    ]

    for cam_name, suffix in cameras:
        image_name = f"snapshot_{timestamp}_{suffix}.png"
        full_path = f"{base_dir}/{image_name}"

        # Python code to be executed within Blender
        code = f"""
import bpy
import os

# 1. Setup Camera
if "{cam_name}" in bpy.data.objects:
    cam = bpy.data.objects["{cam_name}"]
    # Set this camera as the active camera for the scene
    bpy.context.scene.camera = cam
    print(f"Using camera: {cam_name}")
else:
    print(f"Camera '{cam_name}' not found in the scene")

# 2. Render Settings
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = "{full_path}"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# 3. Render
bpy.ops.render.render(write_still=True)
print(f"Snapshot saved to: {full_path}")
"""

        try:
            with socket.create_connection((host, port), timeout=30) as s:
                command = {
                    "type": "execute_code",
                    "params": {
                        "code": code
                    }
                }

                print(f"Sending render command for '{cam_name}' to Blender...")
                s.sendall(json.dumps(command).encode('utf-8'))

                data = s.recv(16384)
                if data:
                    response = json.loads(data.decode('utf-8'))
                    print("Blender response:")
                    print(json.dumps(response, indent=2))

                    if response.get("status") == "success":
                        print(f"Snapshot '{suffix}' process completed successfully.")
                    else:
                        print(f"Snapshot '{suffix}' process failed.")

        except Exception as e:
            print(f"Error during snapshot for '{cam_name}': {e}")

if __name__ == "__main__":
    take_snapshot()
