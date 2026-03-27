import socket
import json

def get_flag_post_taffrail_locations():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import json

data = {}
for obj in bpy.data.objects:
    if "Flagpost" in obj.name or "Dutch_Flag" in obj.name or "Taffrail" in obj.name:
        # Get world matrix
        world_matrix = obj.matrix_world
        # Get location of origin in world space
        world_origin = list(world_matrix.translation)
        
        # Get center of bounding box in world space
        import mathutils
        bbox_center = list(sum((world_matrix @ mathutils.Vector(b) for b in obj.bound_box), mathutils.Vector()) / 8)
        
        data[obj.name] = {
            "origin": world_origin,
            "bbox_center": bbox_center
        }

print(json.dumps(data))
"""

    try:
        with socket.create_connection((host, port), timeout=30) as s:
            command = {
                "type": "execute_code",
                "params": {
                    "code": code
                }
            }
            s.sendall(json.dumps(command).encode('utf-8'))
            data = s.recv(16384)
            if data:
                resp = json.loads(data.decode('utf-8'))
                if 'result' in resp and 'stdout' in resp['result']:
                    print(resp['result']['stdout'])
                else:
                    print(json.dumps(resp, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_flag_post_taffrail_locations()
