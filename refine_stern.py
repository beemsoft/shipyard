import bpy
import mathutils
import json
import socket
import math

def update_stern_refined():
    # 1. Update Fashion Pieces with the new curvature
    # Bottom at Z=2.0 (X=-18.95, Y=0)
    # Lower Part (sideways) at Z=6.0 (X=-19.5, Y=5.0)
    # Upper Part (inward) at Z=12.0 (X=-18.95, Y=4.5)
    
    # Coordinates:
    # (X, Y, Z)
    points_l = [
        (-18.95, 0.0, 2.0),
        (-19.5, -5.0, 6.0),
        (-18.95, -4.5, 12.0)
    ]
    points_r = [
        (-18.95, 0.0, 2.0),
        (-19.5, 5.0, 6.0),
        (-18.95, 4.5, 12.0)
    ]

    def update_curve(name, points):
        obj = bpy.data.objects.get(name)
        if obj and obj.type == 'CURVE':
            spline = obj.data.splines[0]
            # Ensure enough points
            while len(spline.bezier_points) < len(points):
                spline.bezier_points.add(1)
            for i, p in enumerate(points):
                spline.bezier_points[i].co = p
                spline.bezier_points[i].handle_left_type = 'AUTO'
                spline.bezier_points[i].handle_right_type = 'AUTO'
            return obj
        return None

    fashion_l = update_curve("Fashion_Piece_L", points_l)
    fashion_r = update_curve("Fashion_Piece_R", points_r)

    # 2. Regenerate Stern_Transom_Main to fit seamlessly between new fashion ribs
    if fashion_l and fashion_r:
        # Cleanup old transom
        old_transom = bpy.data.objects.get("Stern_Transom_Main")
        if old_transom:
            bpy.data.objects.remove(old_transom, do_unlink=True)
            
        mesh = bpy.data.meshes.new("Stern_Transom_Main_Mesh")
        obj = bpy.data.objects.new("Stern_Transom_Main", mesh)
        bpy.context.collection.objects.link(obj)
        
        verts = []
        faces = []
        
        segments = 100
        z_min, z_max = 2.0, 12.0
        x_pos = -18.95
        thickness = 0.15
        offset = 0.075 # Inward from centerline of 0.15m thick ribs
        
        for i in range(segments + 1):
            t = i / segments
            z = z_min + t * (z_max - z_min)
            
            # Evaluate curves at height Z
            # Sampling logic:
            # We'll use evaluate_bezier which is a method of the Spline, not the object.
            
            def eval_spline_y(spline, z_target):
                # We'll use the bezier_points directly to approximate
                # For 3 points, it's a quadratic Bezier
                p0 = spline.bezier_points[0].co
                p1 = spline.bezier_points[1].co
                p2 = spline.bezier_points[2].co
                
                # Sample 100 points along the curve
                best_y = 0
                min_dist = 1000
                for j in range(101):
                    t = j / 100
                    # B(t) = (1-t)^2*P0 + 2(1-t)t*P1 + t^2*P2
                    # This is only an approximation since we have handles, but for AUTO it's close.
                    z_eval = (1-t)**2 * p0.z + 2*(1-t)*t * p1.z + t**2 * p2.z
                    y_eval = (1-t)**2 * p0.y + 2*(1-t)*t * p1.y + t**2 * p2.y
                    
                    dist = abs(z_eval - z_target)
                    if dist < min_dist:
                        min_dist = dist
                        best_y = y_eval
                return best_y

            y_val_l = eval_spline_y(fashion_l.data.splines[0], z)
            y_val_r = eval_spline_y(fashion_r.data.splines[0], z)
            
            # Apply offset
            y_inner_l = y_val_l + offset
            y_inner_r = y_val_r - offset
            
            # Vertices for the front face (X = -18.95)
            verts.append((x_pos, y_inner_l, z))
            verts.append((x_pos, y_inner_r, z))
            # Vertices for the back face (X = -18.95 + thickness)
            verts.append((x_pos + thickness, y_inner_l, z))
            verts.append((x_pos + thickness, y_inner_r, z))
            
            if i > 0:
                base = (i - 1) * 4
                # Front face
                faces.append((base, base + 1, base + 5, base + 4))
                # Back face
                faces.append((base + 2, base + 3, base + 7, base + 6))
                # Left side
                faces.append((base, base + 4, base + 6, base + 2))
                # Right side
                faces.append((base + 1, base + 5, base + 7, base + 3))
                # Bottom cap (only for first segment)
                if i == 1:
                    faces.append((base, base + 1, base + 3, base + 2))
                # Top cap (only for last segment)
                if i == segments:
                    faces.append((base + 4, base + 5, base + 7, base + 6))
                    
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        
        # Material
        mat = bpy.data.materials.get("Rib_Material")
        if mat:
            obj.data.materials.append(mat)

    # 3. Reposition gunports to Z=5.2
    # Cleanup old gunports first (just in case they were applied as booleans, but they should be separate objects for the cutters)
    for obj_name in ["Gunport_Cutter_0", "Gunport_Cutter_1", "Gunport_Cutter_2", "Gunport_Cutter_3"]:
        old_cutter = bpy.data.objects.get(obj_name)
        if old_cutter:
            bpy.data.objects.remove(old_cutter, do_unlink=True)
            
    # Create cutters at Z=5.2
    z_ports = 5.2
    y_positions = [-2.4, -0.8, 0.8, 2.4]
    cutters = []
    
    for i, y in enumerate(y_positions):
        bpy.ops.mesh.primitive_cube_add(size=0.8, location=(-18.95, y, z_ports))
        cutter = bpy.context.active_object
        cutter.name = f"Gunport_Cutter_{i}"
        # Make it thicker than the transom
        cutter.scale = (1.0, 1.0, 1.0) 
        cutters.append(cutter)
        
    # Apply Boolean to Transom
    transom = bpy.data.objects.get("Stern_Transom_Main")
    if transom:
        for cutter in cutters:
            mod = transom.modifiers.new(name=cutter.name, type='BOOLEAN')
            mod.object = cutter
            mod.operation = 'DIFFERENCE'
            mod.solver = 'EXACT'
            # Hide the cutter
            cutter.hide_viewport = True
            cutter.hide_render = True
            # Apply the modifier
            bpy.context.view_layer.objects.active = transom
            bpy.ops.object.modifier_apply(modifier=mod.name)
            # Remove the cutter object
            bpy.data.objects.remove(cutter, do_unlink=True)

    print("Stern refined: fashion ribs updated, transom regenerated, gunports moved to Z=5.2.")

update_stern_refined()
