import socket
import json

def cleanup_shipyard_via_bridge():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy

def cleanup_shipyard():
    # Names of top-level objects to remove
    objs = ["Water_Surface", "Pier", "Treadmill_Crane", "Crane_Jib", "Sun_Light"]
    for name in objs:
        if name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
            
    # Remove scaffolding posts and beams by name pattern
    import re
    # Patterns to match at the beginning of the name
    start_patterns = ["Scaffold_Post_", "Scaffold_Beam_", "Bridge_Scaffold_", "Foremast", "Mainmast", "Mizenmast", "Bowsprit", "Spritsail_Yard", "Mizen_"]
    # Patterns to match anywhere in the name
    anywhere_patterns = ["Top_", "Yard"]
    
    regex_start = re.compile(f"^({'|'.join(start_patterns)}).*")
    regex_anywhere = re.compile(f".*({'|'.join(anywhere_patterns)}).*")
    
    for obj in list(bpy.data.objects):
        if regex_start.match(obj.name) or regex_anywhere.match(obj.name) or obj.name in ["Water_Surface", "Pier"]:
            try:
                mesh = obj.data
                bpy.data.objects.remove(obj, do_unlink=True)
                if mesh and hasattr(mesh, 'name') and mesh.name in bpy.data.meshes:
                    bpy.data.meshes.remove(mesh, do_unlink=True)
            except:
                pass

    # Clean up the collection
    if "Shipyard_Collection" in bpy.data.collections:
        col = bpy.data.collections["Shipyard_Collection"]
        # Remove any remaining objects in the collection
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)

cleanup_shipyard()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("Shipyard cleanup via bridge successful.")
"""

    command = {
        "type": "execute_code",
        "params": {
            "code": code
        }
    }

    try:
        with socket.create_connection((host, port), timeout=10) as s:
            s.sendall(json.dumps(command).encode('utf-8'))
            print("Cleanup command sent via bridge.")
            # We don't strictly need to wait for response if we trust delivery,
            # but let's try to see if it responds.
            try:
                data = s.recv(4096)
                if data:
                    print("Response received:", data.decode('utf-8'))
            except socket.timeout:
                print("Response timed out, but command was likely received.")
    except Exception as e:
        print(f"Error connecting to bridge: {e}")

if __name__ == "__main__":
    cleanup_shipyard_via_bridge()
