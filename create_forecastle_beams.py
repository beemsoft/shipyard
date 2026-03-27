import socket
import json

def create_forecastle_beams():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import mathutils
import math

def create_beam(name, x, width, z, thickness, material_name):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    hw = width
    ht = thickness / 2.0
    
    verts = [
        (x, -hw, z - ht), (x, hw, z - ht), (x, hw, z + ht), (x, -hw, z + ht),
        (x + thickness, -hw, z - ht), (x + thickness, hw, z - ht), (x + thickness, hw, z + ht), (x + thickness, -hw, z + ht)
    ]
    faces = [
        (0,1,2,3), (4,5,6,7), (0,4,7,3), (1,5,6,2), (0,1,5,4), (3,2,6,7)
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    if material_name in bpy.data.materials:
        obj.data.materials.append(bpy.data.materials[material_name])
    return obj

def create_knee(name, x, y, z, size, thickness, orientation, material_name):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    s = size
    t = thickness
    if orientation == 'RIGHT':
        verts = [
            (x, y, z), (x, y - s, z), (x, y - s, z - t), (x, y - t, z - t), (x, y - t, z - s), (x, y, z - s),
            (x + t, y, z), (x + t, y - s, z), (x + t, y - s, z - t), (x + t, y - t, z - t), (x + t, y - t, z - s), (x + t, y, z - s)
        ]
    else: # LEFT
        verts = [
            (x, y, z), (x, y + s, z), (x, y + s, z - t), (x, y + t, z - t), (x, y + t, z - s), (x, y, z - s),
            (x + t, y, z), (x + t, y + s, z), (x + t, y + s, z - t), (x + t, y + t, z - t), (x + t, y + t, z - s), (x + t, y, z - s)
        ]
    
    faces = [
        (0,1,2,3,4,5), (6,7,8,9,10,11),
        (0,6,7,1), (1,7,8,2), (2,8,9,3), (3,9,10,4), (4,10,11,5), (5,11,6,0)
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    if material_name in bpy.data.materials:
        obj.data.materials.append(bpy.data.materials[material_name])
    return obj

# Clean up
for obj in list(bpy.data.objects):
    if obj.name.startswith("Forecastle_Beam_") or obj.name.startswith("Forecastle_Knee_"):
        bpy.data.objects.remove(obj, do_unlink=True)

# Frames are Forecastle_Frame_00 to Forecastle_Frame_07
# X positions: [5.0, 8.0, 11.0, 14.0, 17.0, 19.0, 21.0, 23.0]
# Forecastle deck is typically around 8.5m above keel.

frames_info = [
    {"index": 0, "x": 5.0},
    {"index": 1, "x": 8.0},
    {"index": 2, "x": 11.0},
    {"index": 3, "x": 14.0},
    {"index": 4, "x": 17.0},
    {"index": 5, "x": 19.0},
    {"index": 6, "x": 21.0},
    {"index": 7, "x": 23.0}
]

for frame in frames_info:
    x = frame["x"]
    idx = frame["index"]
    
    # Keel top at this X
    keel_top_z = 0.0
    if "Keel" in bpy.data.objects:
        keel = bpy.data.objects["Keel"]
        ray_origin = mathutils.Vector((x, 0.0, 15.0))
        ray_direction = mathutils.Vector((0.0, 0.0, -1.0))
        inv_world = keel.matrix_world.inverted()
        origin_local = inv_world @ ray_origin
        direction_local = inv_world.to_quaternion() @ ray_direction
        hit, loc, norm, index = keel.ray_cast(origin_local, direction_local)
        if hit:
            world_loc = keel.matrix_world @ loc
            keel_top_z = world_loc.z
        elif x > 18.95:
             if "Stempost" in bpy.data.objects:
                stempost = bpy.data.objects["Stempost"]
                inv_world_s = stempost.matrix_world.inverted()
                origin_local_s = inv_world_s @ ray_origin
                direction_local_s = inv_world_s.to_quaternion() @ ray_direction
                hit_s, loc_s, norm_s, index_s = stempost.ray_cast(origin_local_s, direction_local_s)
                if hit_s:
                    world_loc_s = stempost.matrix_world @ loc_s
                    keel_top_z = world_loc_s.z

    z = keel_top_z + 8.5
    
    # Find width by ray-casting against Flare_R
    beam_width = 0.0
    frame_obj_name = f"Forecastle_Frame_{idx:02d}_Flare_R"
    if frame_obj_name in bpy.data.objects:
        obj = bpy.data.objects[frame_obj_name]
        # Ray cast from center outward
        ray_origin = mathutils.Vector((x, 0.0, z))
        ray_direction = mathutils.Vector((0.0, 1.0, 0.0))
        inv_world = obj.matrix_world.inverted()
        origin_local = inv_world @ ray_origin
        direction_local = inv_world.to_quaternion() @ ray_direction
        
        hit, loc, norm, index = obj.ray_cast(origin_local, direction_local)
        if hit:
            world_loc = obj.matrix_world @ loc
            beam_width = abs(world_loc.y)
        
        if beam_width == 0:
            # Try ray casting from outside inward
            ray_origin_out = mathutils.Vector((x, 10.0, z))
            ray_direction_in = mathutils.Vector((0.0, -1.0, 0.0))
            origin_local_out = inv_world @ ray_origin_out
            direction_local_in = inv_world.to_quaternion() @ ray_direction_in
            hit_in, loc_in, norm_in, index_in = obj.ray_cast(origin_local_out, direction_local_in)
            if hit_in:
                world_loc_in = obj.matrix_world @ loc_in
                beam_width = abs(world_loc_in.y)
        
        if beam_width == 0:
            # Try ray casting from top downward (if height is slightly off)
            ray_origin_top = mathutils.Vector((x, 10.0, z + 2.0))
            ray_direction_down = mathutils.Vector((0.0, -1.0, -0.2)).normalized()
            origin_local_top = inv_world @ ray_origin_top
            direction_local_down = inv_world.to_quaternion() @ ray_direction_down
            hit_down, loc_down, norm_down, index_down = obj.ray_cast(origin_local_top, direction_local_down)
            if hit_down:
                world_loc_down = obj.matrix_world @ loc_down
                beam_width = abs(world_loc_down.y)

    if beam_width > 0:
        beam_name = f"Forecastle_Beam_{idx:02d}"
        create_beam(beam_name, x, beam_width, z, 0.25, "Rib_Material")
        
        # Knees
        create_knee(f"Forecastle_Knee_{idx:02d}_R", x, beam_width, z + 0.125, 0.6, 0.18, 'RIGHT', "Rib_Material")
        create_knee(f"Forecastle_Knee_{idx:02d}_L", x, -beam_width, z + 0.125, 0.6, 0.18, 'LEFT', "Rib_Material")
        print(f"Created {{beam_name}} at X={{x}}, width={{beam_width}}")
    else:
        print(f"Missed frame {{frame_obj_name}} for forecastle at Z={{z}}")

print("Created forecastle deck beams and knees.")
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
    create_forecastle_beams()
