import socket
import json

def get_light_status():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import json

data = {}
lights = ["Light_Top", "Light_Side", "Light_Back"]
for name in lights:
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        data[name] = {
            "location": list(obj.location),
            "energy": obj.data.energy,
            "type": obj.data.type,
            "color": list(obj.data.color)
        }
    else:
        data[name] = "Not found"

# Also check World background
world = bpy.context.scene.world
if world:
    data["World"] = {
        "color": list(world.color) if hasattr(world, 'color') else "No color attr",
        "use_nodes": world.use_nodes
    }

print(json.dumps(data))
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
                print("DEBUG: Full response:", json.dumps(response, indent=2))
                print(response.get("stdout", "No stdout"))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_light_status()
