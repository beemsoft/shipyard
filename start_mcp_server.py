import bpy
import time
import threading

# 1. Register the addon if not already
try:
    bpy.ops.preferences.addon_enable(module="addon")
    print("Addon 'addon' enabled.")
except Exception as e:
    print(f"Error enabling addon: {e}")

# 2. Start the MCP server
# The addon defines BLENDERMCP_OT_StartServer operator
server = None
try:
    bpy.ops.blendermcp.start_server()
    print("Blender MCP server started on default port 9876.")
    if hasattr(bpy.types, "blendermcp_server"):
        server = bpy.types.blendermcp_server
except Exception as e:
    print(f"Error starting server operator: {e}")

# 3. Wait to keep the background process alive for a while so we can send commands
print("Blender is running in background. Waiting for 120 seconds to accept commands...")

start_time = time.time()
timeout = 120 # 2 minutes

while time.time() - start_time < timeout:
    # Explicitly check for commands in the queue and run them
    if hasattr(bpy.types, "blendermcp_server") and bpy.types.blendermcp_server:
        server = bpy.types.blendermcp_server
        
        # We know from the addon code that it uses bpy.app.timers.register(execute_wrapper, first_interval=0.0)
        # However, Blender does not provide a public list of registered timers.
        # But wait! The addon.py code for execute_command is what we want to run.
        # If we can't get the command from the thread easily, let's just make sure
        # the main thread is yielding as much as possible.
        pass
    
    # Try to process events that might trigger timers
    try:
        # In 4.0+ redraw_timer might be restricted, but let's try
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    except:
        pass

    time.sleep(0.1)

print("Blender background process timeout reached. Exiting.")
