import sys
import json
import socket
import argparse

def main():
    parser = argparse.ArgumentParser(description='MCP Bridge for Blender Add-on')
    parser.add_argument('--host', default='localhost', help='Blender server host')
    parser.add_argument('--port', type=int, default=9876, help='Blender server port')
    args = parser.parse_args()

    # The stdio-based MCP protocol uses JSON-RPC or similar over stdin/stdout.
    # For Junie to use tools, we'll implement a simple bridge that forwards
    # standard input commands to the Blender TCP socket.

    # However, standard MCP tools are usually listed via a 'list_tools' call.
    # Since we want Junie to "just work", we should probably provide a more
    # complete MCP server implementation here if we were doing it properly.
    
    # For now, let's just create a script that can be used to send a command.
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((args.host, args.port))
        
        # Read from stdin (Junie/Host sending a command)
        for line in sys.stdin:
            if not line.strip():
                continue
            
            try:
                # Forward to Blender
                s.sendall(line.encode('utf-8'))
                
                # Wait for response
                # Note: This is a simplification. Real MCP involves complex handshaking.
                response = s.recv(16384)
                if response:
                    print(response.decode('utf-8'))
                    sys.stdout.flush()
            except Exception as e:
                print(json.dumps({"status": "error", "message": str(e)}))
                sys.stdout.flush()
                break
                
    except Exception as e:
        print(f"Error connecting to Blender: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
