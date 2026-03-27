import os
from PIL import Image

def create_gif(image_folder, output_path, patterns, duration=500):
    # Collect all images matching ALL patterns
    images = []
    
    # Get all files in the folder
    all_files = os.listdir(image_folder)
    
    # Filter files that contain ALL the specified patterns
    files = sorted([f for f in all_files if all(p in f for p in patterns) and f.endswith('.png')])
    
    if not files:
        print(f"No images found for patterns: {patterns}")
        return

    print(f"Found {len(files)} images for {patterns}. Processing...")

    for filename in files:
        img_path = os.path.join(image_folder, filename)
        img = Image.open(img_path)
        # Ensure image is in RGB mode for GIF
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Optionally resize for performance/uniformity
        if not images:
            base_size = img.size
        else:
            if img.size != base_size:
                img = img.resize(base_size, Image.Resampling.LANCZOS)
        
        images.append(img)

    if images:
        # Save as GIF
        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:],
            optimize=True,
            duration=duration,
            loop=0
        )
        print(f"GIF saved successfully at {output_path}")
    else:
        print("No images were processed.")

if __name__ == "__main__":
    folder = "1665/7-provinces/images"
    # Today's date and user perspective
    patterns = ["snapshot_20260320", "user_perspective"]
    output_filename = os.path.join(folder, "timelapse_20260320_user_perspective.gif")
    
    create_gif(folder, output_filename, patterns, duration=300)
