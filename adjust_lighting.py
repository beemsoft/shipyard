import socket
import json

def adjust_lighting():
    host = '127.0.0.1'
    port = 9876
    
    # We will:
    # 1. Delete all existing lights to ensure a fresh setup.
    # 2. Add a strong Area light high above the ship (key light).
    # 3. Add a Point light from the side (port/starboard side).
    # 4. Add a Point light from the back (stern side).
    
    code = """
import bpy

# 1. Clean up existing lights
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

# 2. Add Main Top Area Light (Key Light)
# This covers the whole length of the keel (37.9m) and is positioned high.
bpy.ops.object.light_add(type='AREA', location=(0, 0, 50))
top_light = bpy.context.active_object
top_light.name = "Light_Top"
top_light.data.energy = 50000 # Increased energy for 50m height
top_light.data.size = 80 # Larger size for softer shadows and broad coverage

# 3. Add Side Fill Light (Point)
# Positioned to illuminate the side seen by the main Camera (at Y=-100)
# Height Z=40 for a better downlight angle
bpy.ops.object.light_add(type='POINT', location=(0, -60, 40))
side_light = bpy.context.active_object
side_light.name = "Light_Side"
side_light.data.energy = 20000

# 4. Add Back Light (Point)
# Positioned to illuminate the back seen by Camera_Back (at X=-100)
# Height Z=40 for better visibility of the stern details
bpy.ops.object.light_add(type='POINT', location=(-60, 0, 40))
back_light = bpy.context.active_object
back_light.name = "Light_Back"
back_light.data.energy = 15000

print("Updated lighting setup: Light_Top (Z=50), Light_Side (Z=40), Light_Back (Z=40)")
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
    adjust_lighting()
