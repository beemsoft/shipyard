import socket
import json

def replace_cube_with_sphere():
    host = '127.0.0.1'
    port = 9876
    
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            # Code to delete the 'Cube' and add a 'UVSphere'
            code = """
import bpy
if "Cube" in bpy.data.objects:
    cube = bpy.data.objects["Cube"]
    loc = cube.location.copy()
    bpy.data.objects.remove(cube, do_unlink=True)
    bpy.ops.mesh.primitive_uv_sphere_add(location=loc)
    new_obj = bpy.context.active_object
    new_obj.name = "Sphere"
    print("Replaced Cube with Sphere at", loc)
else:
    print("Cube not found in scene")
"""
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
                print(json.dumps(response, indent=2))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    replace_cube_with_sphere()
