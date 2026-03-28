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

def create_deck(name, num_ribs, start_x, end_x, spacing, material_name, target_z):
    # Create a mesh for the deck
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    verts = []
    faces = []
    
    # Generate vertices along the hull shape, including boundaries
    # We'll sample more points to get a better fit
    num_samples = 40
    sample_spacing = (end_x - start_x + 5.0) / (num_samples - 1)
    current_start_x = start_x - 2.5 # Extend slightly to reach posts
    
    actual_verts_count = 0
    for i in range(num_samples):
        x = current_start_x + (i * sample_spacing)
        
        # 1. Find the exact width by ray-casting against ALL Rib objects AND Stempost/Sternpost
        width = 0.0
        
        # Ray cast from center outwards on Y axis
        ray_origin = mathutils.Vector((x, 0.0, target_z))
        ray_direction = mathutils.Vector((0.0, 1.0, 0.0))
        
        max_hit_y = 0.0
        hit_anything = False
        
        # Check against all Ribs, Stempost, and Sternpost
        targets = [o for o in bpy.data.objects if (o.name.startswith("Rib_") and o.name != "Rib_Profile") or o.name in ["Stempost", "Sternpost"]]
        
        for target in targets:
            inv_world = target.matrix_world.inverted()
            origin_local = inv_world @ ray_origin
            direction_local = inv_world.to_quaternion() @ ray_direction
            
            hit, loc, norm, index = target.ray_cast(origin_local, direction_local)
            if hit:
                world_loc = target.matrix_world @ loc
                max_hit_y = max(max_hit_y, abs(world_loc.y))
                hit_anything = True
        
        if hit_anything:
            width = max_hit_y
            # Left and Right points at the target Z level
            verts.append((x, -width, target_z))
            verts.append((x, width, target_z))
            
            # Create faces (quads)
            if actual_verts_count > 0:
                v_idx = actual_verts_count * 2
                # Quad: (i-1)L, (i)L, (i)R, (i-1)R
                faces.append((v_idx - 2, v_idx, v_idx + 1, v_idx - 1))
            actual_verts_count += 1
            
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    if material_name in bpy.data.materials:
        obj.data.materials.append(bpy.data.materials[material_name])
    
    return obj

# Clean up existing decks
for obj in bpy.data.objects:
    if obj.name.startswith("Main_Deck") or obj.name.startswith("Lower_Deck"):
        bpy.data.objects.remove(obj, do_unlink=True)

# Material
if "Deck_Material" not in bpy.data.materials:
    mat = bpy.data.materials.new(name="Deck_Material")
    mat.diffuse_color = (0.3, 0.2, 0.1, 1.0) # Lighter wood
else:
    mat = bpy.data.materials["Deck_Material"]

# Get Keel top Z at center to define lower deck height (3.5m above keel)
lower_deck_z = 3.5
if "Keel" in bpy.data.objects:
    keel = bpy.data.objects["Keel"]
    import mathutils
    ray_origin = mathutils.Vector((0.0, 0.0, 10.0))
    ray_direction = mathutils.Vector((0.0, 0.0, -1.0))
    inv_world = keel.matrix_world.inverted()
    origin_local = inv_world @ ray_origin
    direction_local = inv_world.to_quaternion() @ ray_direction
    hit, loc, norm, index = keel.ray_cast(origin_local, direction_local)
    if hit:
        world_loc = keel.matrix_world @ loc
        lower_deck_z = world_loc.z + 3.5

# Create the lower deck (flat)
create_deck("Lower_Deck", {num_ribs}, -17.5, 17.5, 2.5, "Deck_Material", lower_deck_z)

print(f"Created flat Lower Deck at Z={{lower_deck_z}} with improved fitting.")
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
