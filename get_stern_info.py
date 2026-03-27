import socket
import json

def get_stern_info():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import json

def get_obj_info(name_contains):
    objs = [obj for obj in bpy.data.objects if name_contains.lower() in obj.name.lower()]
    return [(obj.name, list(obj.location)) for obj in objs]

stern_parts = {
    "Taffrail": get_obj_info("Taffrail"),
    "Upper_Rail": get_obj_info("Stern_Upper_Rail"),
    "Poop": get_obj_info("Poop_Deck"),
    "Mizen": get_obj_info("Mizenmast_Lower")
}

print(json.dumps(stern_parts))
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
                print(response.get("result", {}).get("result", "No result"))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_stern_info()
