# Build Log - March 15, 2026

## Achievements: Ship Foundation and Enhanced Snapshot Process

### 1. Design Assistance Reference
- **Resource:** `20250821_115101.jpg`
- **Description:** A schematic drawing ("SCHEMATISCHE TEKENING ZEVEN PROVINCIËN") used as the primary reference for the ship's proportions, sail plan, and structural geometry. This document provides the historical basis for the 1:1 scale model.

### 2. Base Frame Construction
- **Objective:** Establish the foundational structure of the "7-provinces" ship model.
- **Achievement:** Successfully modeled the core frame components including:
  - **Keel:** The central structural member.
  - **Sternpost and Stempost:** Defining the rear and front profiles.
  - **Hull Base:** Initial curved geometry for the ship's hull.

### 3. User Perspective Camera Integration
- **Objective:** Allow snapshots to be taken from the current 3D viewport's perspective.
- **Achievement:** Developed `capture_viewport_camera.py`, which retrieves the exact location and orientation of the user's view in Blender and creates/updates a Blender camera named `User_Perspective_Camera`.

### 4. "Full View" Camera Adjustment
- **Objective:** Ensure the entire model is captured when viewing from the user's perspective, specifically the stern and bow.
- **Achievement:** Created `capture_viewport_camera_full.py`. This script is an enhancement that automatically shifts the user perspective camera 15 units backwards along its local Z-axis. This ensures a comprehensive view of the entire 17-provinces model.

### 5. High-Quality Renders with EEVEE
- **Objective:** Render snapshots with realistic shading, lighting, and materials.
- **Achievement:** Updated `take_snapshot.py` to use the `BLENDER_EEVEE` render engine. This transition ensures all snapshots reflect the current materials and lighting setup, providing a more accurate visual representation of the build progress compared to the previous viewport-style renders.

### 6. Consolidated Snapshot Workflow
- **Objective:** Streamline the snapshot process to provide the most useful views without redundancy.
- **Achievement:** Refined the camera list in `take_snapshot.py` to three primary views:
  - **Side View:** Captured from the main scene camera.
  - **Back View:** Captured from `Camera_Back` to monitor the stern.
  - **User Perspective:** Captured from `User_Perspective_Camera_Full`, ensuring the user's custom angle is preserved while guaranteeing full model visibility.

### 8. Hull Ribs (Spanten) Modeling
- **Objective:** Define the transverse shape of the hull at regular intervals along the keel.
- **Achievement:** Created `create_hull_ribs.py`, which generates 15 primary hull ribs. 
  - Each rib is a symmetric U-shaped Bezier curve with thickness.
  - The profiles vary dynamically along the keel's length (widest at the center, tapering toward the bow and stern) to establish the ship's volumetric form.

### 9. Automation and Verification
- **Process:**
  1. User positions the viewport in Blender.
  2. Run `python capture_viewport_camera_full.py`.
  3. Run `python take_snapshot.py`.
- **Outcome:** A set of three timestamped PNG images are generated in the `1666/7-provinces/images` directory, documenting the current state of the 3D model with full material details.
