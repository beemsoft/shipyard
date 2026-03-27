import socket
import json

def list_all_objects():
    host = '127.0.0.1'
    port = 9876
    
    code = """
import bpy
import json
res = [obj.name for obj in bpy.data.objects]
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
                    try:
                        # Try to parse the result as JSON if it's a JSON string
                        parsed_output = json.loads(output)
                        print(json.dumps(parsed_output, indent=2))
                    except:
                        print(output)
                else:
                    print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_all_objects()
