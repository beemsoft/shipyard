import socket
import json

def get_keel_top_z():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import mathutils
import json

keel = bpy.data.objects.get("Keel")
if keel:
    # Test points
    x_coords = [-17.5, -10.0, 0.0, 10.0, 17.5]
    results = {}
    for x in x_coords:
        # Cast a ray from high up down towards the keel
        # Keel's center is at Y=0.0
        # Ray origin should be in object local space or world space? 
        # ray_cast uses object space if no matrix is provided.
        
        # World space ray_cast
        ray_origin = mathutils.Vector((x, 0.0, 10.0))
        ray_direction = mathutils.Vector((0.0, 0.0, -1.0))
        
        # For object-space ray_cast, we need to transform the ray
        inv_world = keel.matrix_world.inverted()
        origin_local = inv_world @ ray_origin
        direction_local = inv_world.to_quaternion() @ ray_direction
        
        hit, loc, norm, index = keel.ray_cast(origin_local, direction_local)
        if hit:
            world_loc = keel.matrix_world @ loc
            results[str(x)] = world_loc.z
        else:
            results[str(x)] = "No hit"
    print(json.dumps(results))
else:
    print("Keel not found")
"""
    try:
        with socket.create_connection((host, port), timeout=10) as s:
            command = {"type": "execute_code", "params": {"code": code}}
            s.sendall(json.dumps(command).encode('utf-8'))
            data = s.recv(16384)
            if data:
                print(data.decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_keel_top_z()
