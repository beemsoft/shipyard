import socket
import json

def create_decks():
    host = '127.0.0.1'
    port = 9876

    # Real-size dimensions (should match ribs)
    keel_length = 37.9
    half_length = keel_length / 2.0
    num_ribs = 15
    rib_spacing = keel_length / (num_ribs - 1)
    
    # Python code for Blender
    code = f"""
import bpy
import mathutils
import math

def create_deck(name, num_ribs, half_length, rib_spacing, material_name):
    # Create a mesh for the deck
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    verts = []
    faces = []
    
    # Generate vertices along the top of each rib
    for i in range(num_ribs):
        x = -half_length + (i * rib_spacing)
        t = x / half_length
        factor = math.sqrt(max(0, 1 - t**2))
        
        max_width = 7.0
        max_height = 8.0
        
        width = 1.5 + (max_width - 1.5) * factor
        height = 3.0 + (max_height - 3.0) * factor
        
        # Left and Right points at the top of the rib (deck level)
        # Note: In our ribs, deck level was the last point (x, width, height)
        verts.append((x, -width, height))
        verts.append((x, width, height))
        
        # Create faces (quads) between ribs
        if i > 0:
            v_idx = i * 2
            # Quad: (i-1)L, (i)L, (i)R, (i-1)R
            faces.append((v_idx - 2, v_idx, v_idx + 1, v_idx - 1))
            
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    if material_name in bpy.data.materials:
        obj.data.materials.append(bpy.data.materials[material_name])
    
    return obj

# Clean up existing decks
for obj in bpy.data.objects:
    if obj.name.startswith("Main_Deck"):
        bpy.data.objects.remove(obj, do_unlink=True)

# Material
if "Deck_Material" not in bpy.data.materials:
    mat = bpy.data.materials.new(name="Deck_Material")
    mat.diffuse_color = (0.3, 0.2, 0.1, 1.0) # Lighter wood
else:
    mat = bpy.data.materials["Deck_Material"]

# Create the main deck
create_deck("Main_Deck", {num_ribs}, {half_length}, {rib_spacing}, "Deck_Material")

print("Created Main Deck.")
"""

    try:
        with socket.create_connection((host, port), timeout=30) as s:
            command = {
                "type": "execute_code",
                "params": {
                    "code": code
                }
            }
            s.sendall(json.dumps(command).encode('utf-8'))
            data = s.recv(16384)
            if data:
                print(json.dumps(json.loads(data.decode('utf-8')), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_decks()
