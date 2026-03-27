import socket
import json

def get_bbox():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import mathutils
import json

def get_bounding_box():
    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')
    
    found = False
    for obj in bpy.data.objects:
        # Exclude cameras and lights
        if obj.type not in ['MESH', 'CURVE', 'SURFACE', 'FONT', 'META']:
            continue
            
        found = True
        # Check if object has bound_box
        if hasattr(obj, 'bound_box'):
            for corner in obj.bound_box:
                world_corner = obj.matrix_world @ mathutils.Vector(corner)
                min_x = min(min_x, world_corner.x)
                min_y = min(min_y, world_corner.y)
                min_z = min(min_z, world_corner.z)
                max_x = max(max_x, world_corner.x)
                max_y = max(max_y, world_corner.y)
                max_z = max(max_z, world_corner.z)
    
    if not found:
        return None
    return {'min': [min_x, min_y, min_z], 'max': [max_x, max_y, max_z]}

bbox = get_bounding_box()
print(f'BOUNDING_BOX: {json.dumps(bbox)}')
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
                print(response["result"]["result"])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_bbox()
