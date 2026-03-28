import socket
import json
import os

def apply_stern_texture():
    host = '127.0.0.1'
    port = 9876

    texture_path = r"C:\Users\hpbee\IdeaProjects\Blender\shipyard\1665\7-provinces\images\textures\stern_transom_texture.png"
    texture_path = texture_path.replace("\\", "\\\\") # Escape for JSON string in code

    code = f"""
import bpy
import bmesh

def apply_texture():
    obj = bpy.data.objects.get("Stern_Transom_Main")
    if not obj:
        print("Error: Stern_Transom_Main not found")
        return

    # 1. Create or get Material
    mat_name = "Stern_Transom_Material"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear existing nodes
    nodes.clear()
    
    # Create nodes
    node_tex = nodes.new(type='ShaderNodeTexImage')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    
    node_bsdf.location = (200, 0)
    node_out.location = (400, 0)
    
    # Load Image
    img_path = r"{texture_path}"
    try:
        img = bpy.data.images.load(img_path)
        node_tex.image = img
    except Exception as e:
        print(f"Error loading image: {{e}}")
        return

    # Link nodes
    links.new(node_tex.outputs['Color'], node_bsdf.inputs['Base Color'])
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # 2. Assign Material to Object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    # 3. Smart UV Project for the object
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Project from Back view for better alignment with the texture
    # We use a manual projection since we can't reliably call project_from_view without a 3D Viewport context
    
    # Switch to bmesh to adjust UVs
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    uv_layer = bm.loops.layers.uv.verify()
    
    # Calculate bounds for normalization
    # Transom is in Y-Z plane at X=-18.95
    y_coords = [v.co.y for v in bm.verts]
    z_coords = [v.co.z for v in bm.verts]
    y_min, y_max = min(y_coords), max(y_coords)
    z_min, z_max = min(z_coords), max(z_coords)
    y_range = y_max - y_min if y_max != y_min else 1.0
    z_range = z_max - z_min if z_max != z_min else 1.0

    for face in bm.faces:
        for loop in face.loops:
            v = loop.vert
            # Normalize Y and Z to 0-1 range for UVs
            # Y is horizontal, Z is vertical
            # Flip Y because the texture view is from behind (Back view)
            # Re-flipped to fulfill the horizontal flip request
            loop[uv_layer].uv.x = (v.co.y - y_min) / y_range
            # Flip Z as well (flipped vertically as requested)
            # and move 20% down (add 0.20 to the image coordinate)
            loop[uv_layer].uv.y = 1.0 - (v.co.z - z_min) / z_range + 0.20
            
    bmesh.update_edit_mesh(me)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print("Applied stern texture to Stern_Transom_Main")

apply_texture()
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
                response = json.loads(data.decode('utf-8'))
                print("Blender response:")
                print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    apply_stern_texture()
