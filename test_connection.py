import socket
import json
import sys

def test_blender_connection():
    host = '127.0.0.1'
    port = 9876
    
    print(f"Attempting to connect to Blender MCP server at {host}:{port}...")
    
    try:
        # Create a socket connection
        with socket.create_connection((host, port), timeout=5) as s:
            print("Successfully connected to the socket.")
            
            # Prepare a simple command to check scene info
            command = {
                "type": "get_scene_info",
                "params": {}
            }
            
            # Send the command
            print("Sending 'get_scene_info' command...")
            s.sendall(json.dumps(command).encode('utf-8'))
            
            # Receive response
            data = s.recv(16384)
            if not data:
                print("No data received from server.")
                return
                
            response = json.loads(data.decode('utf-8'))
            print("Received response from Blender:")
            print(json.dumps(response, indent=2))
            
    except ConnectionRefusedError:
        print("Error: Connection refused. Is the Blender MCP server running and listening on port 9876?")
    except socket.timeout:
        print("Error: Connection timed out.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_blender_connection()
