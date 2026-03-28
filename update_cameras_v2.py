import socket
import json
import math

def adjust_cameras():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import math

def update_cameras():
    # 1. Side_Camera (Full ship view)
    # Move it even further back for full ship view with all masts
    if "Side_Camera" in bpy.data.objects:
        cam = bpy.data.objects["Side_Camera"]
        cam.location = (0, -100, 30) # A bit closer than -120, lower than 35
        cam.rotation_euler = (math.radians(80), 0, 0)
        cam.data.lens = 35 
    
    # 2. Camera_Back (Stern focus)
    # Move it more behind the stern but slightly to the left/side for perspective
    if "Camera_Back" in bpy.data.objects:
        cam = bpy.data.objects["Camera_Back"]
        # Stern is at X=-19.5 approx. Let's move further back along X.
        cam.location = (-55, -45, 20) # A bit closer than -65, lower than 25
        cam.rotation_euler = (math.radians(78), 0, math.radians(-120))
        cam.data.lens = 45

    # 3. Camera (Bow focus) - Keep similar but slightly adjusted
    if "Camera" in bpy.data.objects:
        cam = bpy.data.objects["Camera"]
        cam.location = (55, -45, 15)
        cam.rotation_euler = (math.radians(75), 0, math.radians(50))
        cam.data.lens = 35

update_cameras()
print("Cameras updated for better framing.")
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
    adjust_cameras()
