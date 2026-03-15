import socket
import json

def list_all_objects():
    host = '127.0.0.1'
    port = 9876
    
    code = """
import bpy
import json
res = []
for obj in bpy.data.objects:
    res.append({
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "hide_render": obj.hide_render,
        "hide_viewport": obj.hide_viewport
    })
print(json.dumps(res))
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
            data = s.recv(32768)
            if data:
                response = json.loads(data.decode('utf-8'))
                if response.get("status") == "success":
                    # The bridge usually returns the result as a string from stdout
                    output = response.get("result", "")
                    print(output)
                else:
                    print(response)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_all_objects()
