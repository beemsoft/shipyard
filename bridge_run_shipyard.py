import socket
import json
import os
import time

def run_via_bridge():
    host = '127.0.0.1'
    port = 9876
    
    # Shipyard generation code to be sent via bridge
    code = """
import bpy
import math

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

# Setup Collection
shipyard_col = bpy.data.collections.get("Shipyard_Collection")
if not shipyard_col:
    shipyard_col = bpy.data.collections.new("Shipyard_Collection")
    bpy.context.scene.collection.children.link(shipyard_col)

# 1. Water Surface
if "Water_Surface" not in bpy.data.objects:
    bpy.ops.mesh.primitive_plane_add(size=150.0, location=(0, 0, -1.0))
    water = bpy.context.active_object
    water.name = "Water_Surface"
    water_mat = create_material("Water_Material", (0.02, 0.05, 0.1, 1.0), roughness=0.1)
    water.data.materials.append(water_mat)
    if water.name not in shipyard_col.objects[:]:
        shipyard_col.objects.link(water)
    if water.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(water)

# 2. Pier
if "Pier" not in shipyard_col.objects:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-10, -15, 0))
    pier = bpy.context.active_object
    pier.name = "Pier"
    pier.scale = (80.0, 15.0, 2.0)
    pier_mat = create_material("Dark_Wood", (0.1, 0.06, 0.04, 1.0))
    pier.data.materials.append(pier_mat)
    if pier.name not in shipyard_col.objects[:]:
        shipyard_col.objects.link(pier)
    if pier.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(pier)

# 3. Scaffolding (Simplified for bridge test)
dark_wood = bpy.data.materials.get("Dark_Wood")
for i in range(5):
    x_pos = -15 + (i * 8.0)
    for side in [-1, 1]:
        y_pos = side * 7.5
        name = f"Bridge_Scaffold_{i}_{side}"
        if name not in bpy.data.objects:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=10.0, location=(x_pos, y_pos, 4.0))
            post = bpy.context.active_object
            post.name = name
            post.data.materials.append(dark_wood)
            if post.name not in shipyard_col.objects[:]:
                shipyard_col.objects.link(post)
            if post.name in bpy.context.scene.collection.objects:
                bpy.context.scene.collection.objects.unlink(post)

# 4. Save
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("Shipyard generation via bridge successful.")
"""

    command = {
        "type": "execute_code",
        "params": {
            "code": code
        }
    }

    print(f"Connecting to Blender MCP bridge on {host}:{port}...")
    try:
        with socket.create_connection((host, port), timeout=10) as s:
            print("Connected. Sending command...")
            s.sendall(json.dumps(command).encode('utf-8'))
            
            # Since we are in background mode, we might not get a response immediately
            # if the main thread is busy, but we've sent the data to the buffer.
            print("Command sent. Waiting for response (this might timeout if Blender main thread is locked)...")
            try:
                data = s.recv(4096)
                if data:
                    print("Response received:")
                    print(json.loads(data.decode('utf-8')))
            except socket.timeout:
                print("Response timed out, but command was delivered to the server socket.")
                
    except Exception as e:
        print(f"Bridge connection error: {e}")

if __name__ == "__main__":
    run_via_bridge()
