import socket
import json
import os

def apply_deck_texture():
    host = '127.0.0.1'
    port = 9876

    texture_dir = os.path.abspath(os.path.join('1665', '7-provinces', 'images', 'textures', 'old_planks_02'))

    maps = {
        'diffuse': os.path.join(texture_dir, 'old_planks_02_diffuse_2k.jpg'),
        'normal': os.path.join(texture_dir, 'old_planks_02_nor_gl_2k.jpg'),
        'rough': os.path.join(texture_dir, 'old_planks_02_rough_2k.jpg')
    }

    # Blender Python code
    code = f"""
import bpy
import os

def create_pbr_material(name, maps):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
    
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear nodes
    for node in nodes:
        nodes.remove(node)
        
    # Create Principled BSDF
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    
    # Create Output
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (400, 0)
    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    # Texture Coordinate and Mapping
    node_tex_coord = nodes.new(type='ShaderNodeTexCoord')
    node_tex_coord.location = (-1200, 0)
    
    node_mapping = nodes.new(type='ShaderNodeMapping')
    node_mapping.location = (-1000, 0)
    # Adjust scaling for the ship deck
    node_mapping.inputs['Scale'].default_value[0] = 5.0
    node_mapping.inputs['Scale'].default_value[1] = 5.0
    links.new(node_tex_coord.outputs['UV'], node_mapping.inputs['Vector'])
    
    # Diffuse/Albedo
    if os.path.exists(maps['diffuse']):
        img_diff = bpy.data.images.load(maps['diffuse'])
        node_diff = nodes.new(type='ShaderNodeTexImage')
        node_diff.image = img_diff
        node_diff.location = (-700, 300)
        links.new(node_mapping.outputs['Vector'], node_diff.inputs['Vector'])
        links.new(node_diff.outputs['Color'], node_bsdf.inputs['Base Color'])
        
    # Roughness
    if os.path.exists(maps['rough']):
        img_rough = bpy.data.images.load(maps['rough'])
        node_rough = nodes.new(type='ShaderNodeTexImage')
        node_rough.image = img_rough
        node_rough.image.colorspace_settings.name = 'Non-Color'
        node_rough.location = (-700, 0)
        links.new(node_mapping.outputs['Vector'], node_rough.inputs['Vector'])
        links.new(node_rough.outputs['Color'], node_bsdf.inputs['Roughness'])
        
    # Normal
    if os.path.exists(maps['normal']):
        img_nor = bpy.data.images.load(maps['normal'])
        node_nor = nodes.new(type='ShaderNodeTexImage')
        node_nor.image = img_nor
        node_nor.image.colorspace_settings.name = 'Non-Color'
        node_nor.location = (-700, -300)
        
        node_nor_map = nodes.new(type='ShaderNodeNormalMap')
        node_nor_map.location = (-400, -300)
        
        links.new(node_mapping.outputs['Vector'], node_nor.inputs['Vector'])
        links.new(node_nor.outputs['Color'], node_nor_map.inputs['Color'])
        links.new(node_nor_map.outputs['Normal'], node_bsdf.inputs['Normal'])
        
    return mat

maps = {{
    'diffuse': r"{maps['diffuse']}",
    'normal': r"{maps['normal']}",
    'rough': r"{maps['rough']}"
}}

mat = create_pbr_material("Deck_Planks_Material", maps)

# Apply to Main_Deck and any other deck objects
deck_keywords = ["deck", "poop", "forecastle"]
for obj in bpy.data.objects:
    if any(k in obj.name.lower() for k in deck_keywords):
        if obj.type == 'MESH':
            if len(obj.data.materials) == 0:
                obj.data.materials.append(mat)
            else:
                obj.data.materials[0] = mat
            
            # Ensure UV map exists for textures
            if not obj.data.uv_layers:
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
                bpy.ops.object.mode_set(mode='OBJECT')

print("Applied old_planks_02 material to deck objects.")
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
    apply_deck_texture()
