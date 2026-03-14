# Shipyard Project

The **Shipyard** project aims to create ship models in Blender by leveraging the power of AI agents. By combining Blender's robust 3D modeling capabilities with the reasoning and automation of AI models, we can streamline the creation of complex maritime assets.

The first step of this project is to establish a seamless interaction workflow between AI agents (like Junie, Claude, or Copilot) and Blender, enabling real-time scene manipulation and automated script execution.

# Why Blender MCP Addon?

While IntelliJ and Junie support standard Model Context Protocol (MCP) servers, we use a dedicated **Blender MCP Addon** (`addon.py`) for several critical reasons:

1.  **Direct `bpy` Access**: The addon runs directly within Blender's Python environment. This provides immediate access to the full `bpy` (Blender Python API) without needing complex external RPC (Remote Procedure Call) mechanisms.
2.  **Main Thread Execution**: Blender's API is not thread-safe. By running as an addon, the server can use `bpy.app.timers` to safely schedule commands on Blender's main thread, preventing crashes.
3.  **UI & Viewport Integration**: The addon can capture the active 3D viewport and interact with the user interface, which a standalone external process cannot easily do.
4.  **Real-time Interaction**: It allows Junie to query and modify the scene live as you work, rather than just processing static files.
5.  **Bundled Dependencies**: It simplifies the setup by leveraging the Python environment already bundled with Blender, including all necessary 3D libraries.

# Workflow Comparison: MCP vs. Manual Python Scripts

When using AI (like Junie) to model in Blender, there are two primary workflows. Here is how they compare:

### 1. Using MCP (Model Context Protocol)
In this workflow, Junie communicates directly with the **Blender MCP Addon** running inside Blender.

*   **Feedback Loop**: **Near-instant**. Junie sends a command, Blender executes it via `bpy`, and the result (or error) is returned immediately to Junie.
*   **Interactivity**: Junie can "see" the scene. It can query objects, get their locations, and even take screenshots of the viewport before deciding on the next action.
*   **Error Handling**: If a command fails, Junie receives the traceback immediately and can attempt a fix autonomously.
*   **Context Awareness**: Junie maintains a live connection. If you move an object manually, Junie can refresh its internal state by querying the scene again.
*   **Setup**: Requires installing the `addon.py` and starting the MCP server within Blender.

### 2. Manual Python Scripting
In this workflow, Junie generates a standalone `.py` script, which you then manually load and run in Blender's Text Editor.

*   **Feedback Loop**: **Slow/Manual**. You must copy the code, switch to Blender, open/create a text block, paste the code, and click "Run Script". If there's an error, you must copy it back to Junie.
*   **Interactivity**: **None**. Junie operates "blind". It doesn't know what's currently in your scene unless you manually describe it or provide a file.
*   **Error Handling**: **Disconnected**. You are the "bridge" for error reporting. Junie cannot verify if the script worked until you tell it.
*   **Context Awareness**: **Static**. Junie only knows about the code it generated, not the actual state of the Blender scene after execution.
*   **Setup**: No special setup required, but high manual overhead during the modeling process.

### Summary Table

| Feature | MCP Workflow (Junie + Addon) | Manual Script Workflow |
| :--- | :--- | :--- |
| **Speed** | ⚡ High (Live execution) | 🐢 Low (Copy-paste-run) |
| **Vision** | 👁️ Can take viewport screenshots | 🙈 Blind |
| **State** | 🔄 Real-time scene queries | 📄 Static code generation |
| **Correction** | 🛠️ Automatic self-healing | 👤 Manual error reporting |
| **Complexity** | ⚙️ Requires one-time addon setup | 📝 No setup, high friction |

### Can I still use Python scripts with MCP?
**Yes, absolutely.** 

The MCP workflow is not an "either/or" choice. The Blender MCP Addon includes an `execute_code` tool that allows Junie to send and run complete, multi-line Python scripts directly inside Blender.

*   **Hybrid Power**: You can ask Junie to "Generate a script to create a procedural city and run it." Junie will then write the full script and execute it via the MCP connection in one step.
*   **Direct Execution**: Unlike the manual workflow, you don't need to copy-paste. The code is sent via the bridge and executed immediately on Blender's main thread.
*   **Instant Debugging**: If the generated script has a syntax error or a Blender API conflict, Junie sees the error immediately and can fix the script and re-run it without your intervention.

# Examples

## Modifying Objects via MCP

The following is an example Python script (`change_sphere_to_pyramid.py`) that demonstrates how to use the Blender MCP integration to modify a scene object. This script connects to the running Blender MCP server and executes code to replace a sphere with a pyramid.

```python
import socket
import json

def change_sphere_to_pyramid():
    host = '127.0.0.1'
    port = 9876
    
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            # Code to delete the 'Sphere' and add a 'Cone' with 4 vertices (pyramid)
            code = """
import bpy
if "Sphere" in bpy.data.objects:
    sphere = bpy.data.objects["Sphere"]
    loc = sphere.location.copy()
    bpy.data.objects.remove(sphere, do_unlink=True)
    bpy.ops.mesh.primitive_cone_add(vertices=4, location=loc)
    new_obj = bpy.context.active_object
    new_obj.name = "Pyramid"
    print("Replaced Sphere with Pyramid at", loc)
else:
    print("Sphere not found in scene")
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
                print(json.dumps(response, indent=2))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    change_sphere_to_pyramid()
```

To use this script, ensure the Blender MCP addon is running, then execute the script with Python. It will connect to Blender on localhost:9876 and perform the modification.

# Credits

## Blender
Blender is the free and open-source 3D creation suite. First released on **January 2, 1994**.
[blender.org](https://www.blender.org/)

## Blender MCP
Model Context Protocol (MCP) is an open protocol that enables seamless integration between AI models and their toolsets. Introduced by Anthropic in **November 2024**.
[modelcontextprotocol.io](https://modelcontextprotocol.io/)

## Blender MCP Addon
A powerful Blender extension that implements a TCP-based MCP server to expose Blender's internal state and functions to AI models. Developed by Siddharth Ahuja. This version released in **2025**.
[github.com/ahujasid](https://www.github.com/ahujasid)

Originally designed to bridge Blender with **Claude**, the architecture of this addon is agent-agnostic. It can be utilized by any AI agent that supports the Model Context Protocol (MCP), including **Junie**, through a simple TCP-to-stdio bridge.

## Blender Python API
The foundation for all Blender automation and addon development, allowing full control over scenes, data, and operators. Versioning is tied to Blender releases since **late 1990s**.
[docs.blender.org/api](https://docs.blender.org/api/current/index.html)

## Junie
The autonomous AI agent from JetBrains that facilitates the connection, configuration, and execution of tasks within the Blender environment via MCP. First released in **2024**.
[jetbrains.com](https://www.jetbrains.com/)

## Copilot
An AI-powered code assistant that provides intelligent code suggestions, automation, and integration with development environments. Developed by GitHub. First released in **June 2021**.
[github.com/features/copilot](https://github.com/features/copilot)

## Python
The core programming language used for both the Blender API and the MCP server implementation. First released on **February 20, 1991**.
[python.org](https://www.python.org/)
