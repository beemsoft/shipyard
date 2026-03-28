import socket
import json

def create_masts():
    host = '127.0.0.1'
    port = 9876

    code = """
import bpy
import mathutils
import math

def create_mast_section(name, bottom_z, height, bottom_dia, top_dia, x_pos, rake_deg=0, material_name="Rib_Material"):
    # Create a mesh for the mast section (tapered cylinder)
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    segments = 32
    verts = []
    faces = []
    
    # Rake angle (tilt backward, from Z towards -X)
    # theta is the rotation around Y
    theta = math.radians(-rake_deg)
    
    # Bottom circle (in XY plane, centered at x_pos, 0, bottom_z)
    for i in range(segments):
        a = 2 * math.pi * i / segments
        x_local = math.cos(a) * bottom_dia / 2
        y_local = math.sin(a) * bottom_dia / 2
        
        # Point (x_local, y_local, 0) relative to bottom center
        # Rotate point (x_local, 0, 0) around Y? No, it's a circle in XY plane.
        # We need the cross-section to be perpendicular to the mast axis.
        # If the mast axis is tilted by theta around Y:
        # local vector v = (x_local, y_local, 0)
        # rotated v' = (x_local * cos(theta), y_local, -x_local * sin(theta))
        nx = x_local * math.cos(theta)
        ny = y_local
        nz = -x_local * math.sin(theta)
        
        verts.append((x_pos + nx, ny, bottom_z + nz))
        
    # Top circle (along tilted axis)
    for i in range(segments):
        a = 2 * math.pi * i / segments
        x_local = math.cos(a) * top_dia / 2
        y_local = math.sin(a) * top_dia / 2
        
        # Point (x_local, y_local, height) relative to bottom center, then rotate around (0,0,0) by theta
        # x' = x_local * cos(theta) + height * sin(theta)
        # y' = y_local
        # z' = -x_local * sin(theta) + height * cos(theta)
        nx = x_local * math.cos(theta) + height * math.sin(theta)
        ny = y_local
        nz = -x_local * math.sin(theta) + height * math.cos(theta)
        
        verts.append((x_pos + nx, ny, bottom_z + nz))
        
    # Sides
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append((i, next_i, next_i + segments, i + segments))
        
    # Caps
    faces.append(list(range(segments)))
    faces.append(list(range(segments, 2 * segments))[::-1])
    
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Shade Smooth
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    
    if material_name in bpy.data.materials:
        obj.data.materials.append(bpy.data.materials[material_name])
    return obj

def create_top(name, x, z, size, rake_angle, material_name="Rib_Material"):
    # Simple platform (top)
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    s = size / 2
    t = 0.2
    
    # Vertices for a square platform, tilted by rake angle
    # We rotate around Y axis
    rad = math.radians(-rake_angle)
    c = math.cos(rad)
    s_ang = math.sin(rad)
    
    def rot(vx, vy, vz):
        # Rotate point (vx, vy, vz) around (x, 0, z) by rake_angle
        lx, ly, lz = vx - x, vy, vz - z
        nx = lx * c - lz * s_ang
        nz = lx * s_ang + lz * c
        return (nx + x, ly, nz + z)

    verts = [
        rot(x - s, -s, z), rot(x + s, -s, z), rot(x + s, s, z), rot(x - s, s, z),
        rot(x - s, -s, z + t), rot(x + s, -s, z + t), rot(x + s, s, z + t), rot(x - s, s, z + t)
    ]
    faces = [(0,1,2,3), (4,5,6,7), (0,4,7,3), (1,5,6,2), (0,1,5,4), (3,2,6,7)]
    
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    if material_name in bpy.data.materials:
        obj.data.materials.append(bpy.data.materials[material_name])
    return obj

def create_yard(name, x, y, z, length, center_dia, tip_dia, rotation_y_deg=0, rotation_z_deg=0, material_name="Rib_Material"):
    # Create a mesh for the yard (cylinder)
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    segments = 32
    verts = []
    faces = []
    
    # Simple cylinder along Z-axis (local)
    # Bottom circle
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        verts.append((math.cos(angle) * center_dia / 2, math.sin(angle) * center_dia / 2, -length / 2))
    
    # Top circle
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        verts.append((math.cos(angle) * center_dia / 2, math.sin(angle) * center_dia / 2, length / 2))
        
    # Sides
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append((i, next_i, next_i + segments, i + segments))
        
    # Caps
    faces.append(list(range(segments)))
    faces.append(list(range(segments, 2 * segments))[::-1])
    
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Shade Smooth
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    
    # Position and rotate
    obj.location = (x, y, z)
    obj.rotation_euler[1] = math.radians(rotation_y_deg)
    obj.rotation_euler[2] = math.radians(rotation_z_deg)
    
    if material_name in bpy.data.materials:
        obj.data.materials.append(bpy.data.materials[material_name])
    return obj

# Clean up
def clean_masts_and_yards():
    import bpy
    patterns = ["Mast", "Top_", "Bowsprit", "Yard"]
    # Collect objects to remove
    to_remove = []
    for obj in list(bpy.data.objects):
        if any(p in obj.name for p in patterns):
            to_remove.append(obj)
            
    # Remove objects and their meshes
    for obj in to_remove:
        try:
            mesh = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if mesh and mesh.name in bpy.data.meshes:
                bpy.data.meshes.remove(mesh, do_unlink=True)
        except:
            pass

clean_masts_and_yards()

# Positions and Dimensions (Estimated based on 37.9m keel)
# X: Front is +18.95, Back is -18.95
# Foremast: around X=15
# Mainmast: around X=0
# Mizenmast: around X=-12
# Bowsprit: starts at X=20, angled forward

# 1. Foremast
fore_x = 14.5
fore_rake = 0 # straight up
fore_z = 0.744
top_height = 19.5
create_mast_section("Foremast_Lower", fore_z, top_height - fore_z, 1.2, 1.2, fore_x, fore_rake)
create_top("Foremast_Top", fore_x + top_height*math.sin(math.radians(-fore_rake)), top_height, 3.5, fore_rake)
create_mast_section("Foremast_Topmast", top_height, 12.0, 0.8, 0.8, fore_x + top_height*math.sin(math.radians(-fore_rake)), fore_rake)
create_mast_section("Foremast_Topgallant", top_height + 12.0, 7.0, 0.55, 0.55, fore_x + (top_height + 10)*math.sin(math.radians(-fore_rake)), fore_rake)

# Foremast Yards
create_yard("Foremast_Yard", fore_x, 0, 12.0, 14.0, 0.8, 0.4, rotation_z_deg=90)
create_yard("Foremast_Topsail_Yard", fore_x, 0, 24.0, 10.0, 0.5, 0.25, rotation_z_deg=90)
create_yard("Foremast_Topgallant_Yard", fore_x, 0, 34.0, 6.0, 0.35, 0.18, rotation_z_deg=90)

# 2. Mainmast
main_x = -1.0
main_rake = 0 # straight up
main_z = 0.601
create_mast_section("Mainmast_Lower", main_z, top_height - main_z, 1.4, 1.4, main_x, main_rake)
create_top("Mainmast_Top", main_x + top_height*math.sin(math.radians(-main_rake)), top_height, 4.2, main_rake)
create_mast_section("Mainmast_Topmast", top_height, 14.0, 1.0, 1.0, main_x + top_height*math.sin(math.radians(-main_rake)), main_rake)
create_mast_section("Mainmast_Topgallant", top_height + 14.0, 9.0, 0.7, 0.7, main_x + (top_height + 12.5)*math.sin(math.radians(-main_rake)), main_rake)

# Mainmast Yards
create_yard("Mainmast_Yard", main_x, 0, 15.0, 18.0, 1.0, 0.5, rotation_z_deg=90)
create_yard("Mainmast_Topsail_Yard", main_x, 0, 28.0, 13.0, 0.6, 0.3, rotation_z_deg=90)
create_yard("Mainmast_Topgallant_Yard", main_x, 0, 40.0, 8.0, 0.4, 0.2, rotation_z_deg=90)

# 3. Mizenmast
mizen_x = -13.5
mizen_rake = 0 # straight up
mizen_z = 0.730
create_mast_section("Mizenmast_Lower", mizen_z, top_height - mizen_z, 0.9, 0.9, mizen_x, mizen_rake)
create_top("Mizenmast_Top", mizen_x + top_height*math.sin(math.radians(-mizen_rake)), top_height, 2.8, mizen_rake)
create_mast_section("Mizenmast_Topmast", top_height, 10.0, 0.6, 0.6, mizen_x + top_height*math.sin(math.radians(-mizen_rake)), mizen_rake)

# Mizenmast Yards
create_yard("Mizen_Crossjack_Yard", mizen_x, 0, 14.0, 10.0, 0.5, 0.25, rotation_z_deg=90)
create_yard("Mizen_Topsail_Yard", mizen_x, 0, 24.0, 7.0, 0.35, 0.18, rotation_z_deg=90)

# 4. Bowsprit
bow_x = 14.5 # Rooted at the front of the foremast
bow_z = 7.5 # Lower deck level roughly
bow_length = 22.0 # Reduced length
bow_angle = 32

def create_bowsprit(name, x, z, length, dia, angle_deg):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    segments = 32
    verts = []
    faces = []
    rad = math.radians(angle_deg)
    
    # Orientation: Along X-axis, then rotated around Y (upwards)
    # The 'length' is along the cylinder axis.
    # Radius is dia/2.
    
    for i in range(segments):
        a = 2 * math.pi * i / segments
        y_off = math.sin(a) * dia/2
        z_off = math.cos(a) * dia/2
        
        # Base circle (at dist=0)
        # The cross-section must be perpendicular to the bowsprit axis.
        # Rotating around Y by -angle_deg (upward)
        # Local point: (0, y_off, z_off)
        # Rotation around Y:
        # x' = x*cos(theta) + z*sin(theta)
        # z' = -x*sin(theta) + z*cos(theta)
        # Here x=0, theta = -rad (to rotate UPWARDS towards +X)
        # Wait, if +X is forward, and we want to rotate UP, we rotate around Y.
        # A positive rotation around Y (by right hand rule) from +X goes towards -Z.
        # So for +X to go towards +Z, we need a NEGATIVE rotation around Y.
        theta = -rad
        
        bx = z_off * math.sin(theta)
        bz = z_off * math.cos(theta)
        verts.append((x + bx, y_off, z + bz))
        
        # Top circle (at dist=length)
        # Local point: (length, y_off, z_off)
        tx = length * math.cos(theta) + z_off * math.sin(theta)
        tz = -length * math.sin(theta) + z_off * math.cos(theta)
        verts.append((x + tx, y_off, z + tz))

    for i in range(segments):
        n = (i + 1) % segments
        faces.append((i*2, n*2, n*2+1, i*2+1))
    
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Shade Smooth
    for polygon in mesh.polygons:
        polygon.use_smooth = True
        
    if "Rib_Material" in bpy.data.materials:
        obj.data.materials.append(bpy.data.materials["Rib_Material"])
    return obj

create_bowsprit("Bowsprit", bow_x, bow_z, bow_length, 1.0, bow_angle) # Diameter reduced to 1.0

# Spritsail Yard
# Position it on the bowsprit, further out to be in front of the ship
# Ship front is at X=18.95. Beakhead extends to X=33.5.
# Let's place it at dist=15.0 along the bowsprit
spritsail_dist = 15.0
sy_x = bow_x + math.cos(math.radians(bow_angle)) * spritsail_dist
sy_z = bow_z + math.sin(math.radians(bow_angle)) * spritsail_dist
# Position the yard parallel to the water surface (X-Y plane)
# Increased size to be more proportional to the bow
create_yard("Spritsail_Yard", sy_x, 0, sy_z, 14.0, 0.8, 0.4, rotation_y_deg=90, rotation_z_deg=90)

print("Created masts: Foremast, Mainmast, Mizenmast, and Bowsprit.")
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
    create_masts()
