import subprocess
import time

def run_script(script_name):
    print(f"--- Running {script_name} ---")
    try:
        # Most of these scripts communicate with the Blender MCP server over TCP
        # and are designed to be run from the command line.
        result = subprocess.run(["python", script_name], capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print(f"Error in {script_name}: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"FAILED to run {script_name}: {e}")
        print(f"Output: {e.output}")
        print(f"Error: {e.stderr}")
        return False
    return True

def main():
    # Order of operations for building the 1665 7-Provinces ship model
    scripts = [
        "create_keel.py",
        "create_stempost.py",
        "create_sternpost.py",
        "create_hull_ribs.py",
        "create_quarterdeck_poop_frames.py",
        "create_forecastle_frames.py",
        "draw_flat_bottom.py",
        "create_decks.py",
        "apply_deck_texture.py",
        "correct_rib_beams.py",
        "create_quarterdeck_poop_beams.py",
        "create_forecastle_beams.py",
        "create_beakhead.py",
        "create_bow_bulkhead.py",
        # Stern construction sequence
        "create_stern_transoms.py",
        "create_fashion_pieces.py",
        "create_upper_stern_frames.py",
        "create_stern_galleries.py",
        "create_stern_upper_rails.py",
        # Refinement (includes fashion pieces update, transom regeneration, and gunports moved to Z=5.2)
        "bridge_refine_stern.py",
        "apply_stern_texture.py",
        # Masts and Rigging
        "create_masts.py",
        # Flag
        "create_final_flag.py",
        # Environment and Scene setup
        "optimize_scene.py",
        "setup_cameras.py"
    ]

    print("Starting complete ship build process...")
    start_time = time.time()

    for script in scripts:
        if not run_script(script):
            print(f"Aborting build due to failure in {script}")
            return

    end_time = time.time()
    duration = end_time - start_time
    print(f"--- Ship build completed in {duration:.2f} seconds ---")

    # Final snapshot to verify the build
    print("Taking verification snapshots...")
    run_script("take_snapshot.py")

if __name__ == "__main__":
    main()
