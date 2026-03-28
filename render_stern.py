import socket
import json
import os
from datetime import datetime

def render_stern():
    host = '127.0.0.1'
    port = 9876
    
    # Ensure the images directory exists
    save_dir = r"C:\Users\hpbee\IdeaProjects\Blender\shipyard\1665\7-provinces\images"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"stern_render_{timestamp}.png"
    filepath = os.path.join(save_dir, filename).replace('\\', '/')

    code = f"""
import bpy
import os

def setup_stern_camera():
    # 1. Ensure Camera_Back exists
    cam = bpy.data.objects.get("Camera_Back")
    if not cam:
        cam_data = bpy.data.cameras.new("Camera_Back")
        cam = bpy.data.objects.new("Camera_Back", cam_data)
        bpy.context.collection.objects.link(cam)
    
    # 2. Position it for optimal stern view
    cam.location = [-90.0, -65.0, 40.0]
    cam.data.lens = 35
    cam.data.clip_start = 0.1
    cam.data.clip_end = 2000.0
    
    # 3. Setup Look-at target for stern
    target_name = "Target_Camera_Back"
    target_obj = bpy.data.objects.get(target_name)
    if not target_obj:
        target_obj = bpy.data.objects.new(target_name, None)
        bpy.context.collection.objects.link(target_obj)
    
    target_obj.location = [-18.0, 0.0, 22.0]
    
    # 4. Apply Track To constraint
    for c in cam.constraints:
        if c.type == 'TRACK_TO':
            cam.constraints.remove(c)
    
    ttc = cam.constraints.new(type='TRACK_TO')
    ttc.target = target_obj
    ttc.track_axis = 'TRACK_NEGATIVE_Z'
    ttc.up_axis = 'UP_Y'
    
    return cam

def render_view(camera, path):
    bpy.context.scene.camera = camera
    bpy.context.scene.render.filepath = path
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.eevee.use_shadows = True
    
    bpy.ops.render.render(write_still=True)
    return path

cam = setup_stern_camera()
output_path = "{filepath}"
render_view(cam, output_path)
print(f"Stern render saved to: {{output_path}}")
"""
    
    payload = {
        "type": "execute_code",
        "params": {"code": code}
    }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(60)
            s.connect((host, port))
            s.sendall(json.dumps(payload).encode('utf-8'))
            response = s.recv(1024 * 64)
            print(f"Blender response: {response.decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    render_stern()
