import socket
import json

def change_sphere_to_pyramid():
    host = '127.0.0.1'
    port = 9876
    
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            # Code to delete the 'Sphere' and add a 'Cone' with 4 vertices (pyramid)
            code = """
import bpy
if "Sphere" in bpy.data.objects:
    sphere = bpy.data.objects["Sphere"]
    loc = sphere.location.copy()
    bpy.data.objects.remove(sphere, do_unlink=True)
    bpy.ops.mesh.primitive_cone_add(vertices=4, location=loc)
    new_obj = bpy.context.active_object
    new_obj.name = "Pyramid"
    print("Replaced Sphere with Pyramid at", loc)
else:
    print("Sphere not found in scene")
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
    change_sphere_to_pyramid()</content>
<parameter name="filePath">C:\Users\hpbee\IdeaProjects\Blender\shipyard\change_sphere_to_pyramid.py
