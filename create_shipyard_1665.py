import socket
import json
import os

def create_shipyard_1665():
    host = '127.0.0.1'
    port = 9876
    
    # 1. Shipyard Configuration
    # Water surface size (150m x 150m)
    water_size = 150.0
    # Pier dimensions (80m long, 15m wide)
    pier_length = 80.0
    pier_width = 15.0
    pier_height = 2.0
    
    # Scaffolding: 15 ribs around the hull
    # The '7-provinces' ship is approx 37.9m long and 12m wide.
    # Its keel is at X=0, Y=0 (centered longitudinally).
    
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            code = f"""
import bpy
import math
import random

def create_material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = color
            bsdf.inputs['Roughness'].default_value = roughness
            bsdf.inputs['Metallic'].default_value = metallic
    return mat

def cleanup_shipyard():
    objs = ["Water_Surface", "Pier", "Scaffolding_Group", "Treadmill_Crane"]
    for name in objs:
        if name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    # Also clean up collections if needed
    if "Shipyard_Collection" in bpy.data.collections:
        col = bpy.data.collections["Shipyard_Collection"]
        for obj in col.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)

# 0. Setup Collection
shipyard_col = bpy.data.collections.get("Shipyard_Collection")
if not shipyard_col:
    shipyard_col = bpy.data.collections.new("Shipyard_Collection")
    bpy.context.scene.collection.children.link(shipyard_col)

# 1. Water Surface (Calm Harbor)
if "Water_Surface" not in bpy.data.objects:
    bpy.ops.mesh.primitive_plane_add(size={water_size}, location=(0, 0, -1.0))
    water = bpy.context.active_object
    water.name = "Water_Surface"
    water_mat = create_material("Water_Material", (0.02, 0.05, 0.1, 1.0), roughness=0.1)
    water.data.materials.append(water_mat)
    shipyard_col.objects.link(water)
    bpy.context.scene.collection.objects.unlink(water)

# 2. Wooden Pier / Dock
if "Pier" not in shipyard_col.objects:
    # Positioned alongside the ship (ship is at Y=0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-10, -15, 0))
    pier = bpy.context.active_object
    pier.name = "Pier"
    pier.scale = ({pier_length}, {pier_width}, {pier_height})
    pier_mat = create_material("Dark_Wood", (0.1, 0.06, 0.04, 1.0))
    pier.data.materials.append(pier_mat)
    shipyard_col.objects.link(pier)
    bpy.context.scene.collection.objects.unlink(pier)

# 3. Scaffolding around the Ship
# Ship is centered at X=0, approx 38m long. Keel is at Z=0.4 approx.
scaffold_spacing = 4.0
ship_length = 38.0
ship_width = 12.0
for i in range(10):
    x_pos = -ship_length/2 + (i * scaffold_spacing)
    # Side scaffolds (left and right)
    for side in [-1, 1]:
        y_pos = side * (ship_width/2 + 1.5)
        name = f"Scaffold_Post_{{i}}_{{side}}"
        if name not in bpy.data.objects:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=12.0, location=(x_pos, y_pos, 5.0))
            post = bpy.context.active_object
            post.name = name
            post.data.materials.append(bpy.data.materials["Dark_Wood"])
            shipyard_col.objects.link(post)
            bpy.context.scene.collection.objects.unlink(post)
            
            # Horizontal beams (platforms)
            for h in [3.0, 6.0, 9.0]:
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_pos, y_pos, h))
                beam = bpy.context.active_object
                beam.scale = (scaffold_spacing, 1.0, 0.1)
                beam.name = f"Scaffold_Beam_{{i}}_{{side}}_{{h}}"
                beam.data.materials.append(bpy.data.materials["Dark_Wood"])
                shipyard_col.objects.link(beam)
                bpy.context.scene.collection.objects.unlink(beam)

# 4. Treadmill Crane (Simplified 17th Century Style)
if "Treadmill_Crane" not in shipyard_col.objects:
    # A large wooden structure with a jib
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-25, -20, 4.0))
    crane_base = bpy.context.active_object
    crane_base.name = "Treadmill_Crane"
    crane_base.scale = (4.0, 4.0, 8.0)
    crane_base.data.materials.append(bpy.data.materials["Dark_Wood"])
    shipyard_col.objects.link(crane_base)
    bpy.context.scene.collection.objects.unlink(crane_base)
    
    # Crane Jib
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-25, -20, 12.0))
    jib = bpy.context.active_object
    jib.name = "Crane_Jib"
    jib.scale = (10.0, 0.5, 0.5)
    jib.rotation_euler[1] = math.radians(-30)
    jib.data.materials.append(bpy.data.materials["Dark_Wood"])
    shipyard_col.objects.link(jib)
    bpy.context.scene.collection.objects.unlink(jib)

# 5. Environment Lighting (Warm afternoon sun)
if "Sun_Light" not in bpy.data.objects:
    bpy.ops.object.light_add(type='SUN', location=(50, 50, 50))
    sun = bpy.context.active_object
    sun.name = "Sun_Light"
    sun.data.energy = 5.0
    sun.data.color = (1.0, 0.9, 0.7)
    sun.rotation_euler = (math.radians(45), 0, math.radians(135))

print("1665 Shipyard Scenery Generated.")
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
                print("Blender response:")
                print(json.dumps(response, indent=2))
            
    except Exception as e:
        print(f"Error: {e}")
        print("Falling back: Script written to disk for manual execution if Blender is not connected.")

if __name__ == "__main__":
    create_shipyard_1665()
