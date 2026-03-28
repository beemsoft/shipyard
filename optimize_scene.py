import socket
import json
import math

def adjust_scene():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import math

def setup_lighting():
    # Remove existing lights
    for obj in [o for o in bpy.data.objects if o.type == 'LIGHT']:
        bpy.data.objects.remove(obj, do_unlink=True)
            
    # 1. Key Light (Sun)
    sun_data = bpy.data.lights.new(name="Sun_Key", type='SUN')
    sun_data.energy = 5.0
    sun_data.angle = math.radians(0.5)
    sun_obj = bpy.data.objects.new(name="Sun_Key", object_data=sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.location = (50, -50, 50)
    # Point towards the center of the ship (around 0,0,15)
    # To point (50,-50,50) at (0,0,15): direction is (-50, 50, -35)
    # Roughly 45 deg down, 45 deg from front-right
    sun_obj.rotation_euler = (math.radians(55), 0, math.radians(45))
    
    # 2. Fill Light (Area)
    fill_data = bpy.data.lights.new(name="Fill_Area", type='AREA')
    fill_data.energy = 5000.0
    fill_data.size = 20.0
    fill_obj = bpy.data.objects.new(name="Fill_Area", object_data=fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-50, -50, 30)
    fill_obj.rotation_euler = (math.radians(60), 0, math.radians(-45))
    
    # 3. Rim Light (Area) - Highlights masts and ship profile from back/top
    rim_data = bpy.data.lights.new(name="Rim_Area", type='AREA')
    rim_data.energy = 8000.0
    rim_data.size = 30.0
    rim_obj = bpy.data.objects.new(name="Rim_Area", object_data=rim_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (0, 60, 60)
    rim_obj.rotation_euler = (math.radians(135), 0, 0)

    # 4. Stern Fill (Point) - Specifically for the refined stern
    stern_fill_data = bpy.data.lights.new(name="Stern_Fill", type='POINT')
    stern_fill_data.energy = 2000.0
    stern_fill_obj = bpy.data.objects.new(name="Stern_Fill", object_data=stern_fill_data)
    bpy.context.collection.objects.link(stern_fill_obj)
    stern_fill_obj.location = (-30, -20, 10)

def setup_cameras():
    # 1. Side_Camera (Full ship view)
    if "Side_Camera" in bpy.data.objects:
        cam = bpy.data.objects["Side_Camera"]
        cam.location = (0, -110, 25)
        cam.rotation_euler = (math.radians(85), 0, 0)
        cam.data.lens = 35
    
    # 2. Camera_Back (Stern focus)
    if "Camera_Back" in bpy.data.objects:
        cam = bpy.data.objects["Camera_Back"]
        cam.location = (-60, -25, 20) # Angled view of stern
        cam.rotation_euler = (math.radians(75), 0, math.radians(-110))
        cam.data.lens = 45

    # 3. Camera (Bow focus)
    if "Camera" in bpy.data.objects:
        cam = bpy.data.objects["Camera"]
        cam.location = (65, -45, 25)
        cam.rotation_euler = (math.radians(75), 0, math.radians(55))
        cam.data.lens = 35

    # 4. User_Perspective_Camera_Full (Overview)
    if "User_Perspective_Camera_Full" in bpy.data.objects:
        cam = bpy.data.objects["User_Perspective_Camera_Full"]
        cam.location = (85, -95, 65)
        cam.rotation_euler = (math.radians(65), 0, math.radians(40))
        cam.data.lens = 28

setup_lighting()
setup_cameras()
print("Lighting and Cameras optimized for the 1665 ship model.")
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
    adjust_scene()
