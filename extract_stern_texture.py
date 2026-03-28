from PIL import Image
import os

def extract_stern_texture(input_path, output_path):
    # Open the image
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    img = Image.open(input_path)
    
    # Based on looking at the image 20250821_115239.jpg:
    # The image is 4000x3000. It's rotated (the ship's stern is sideways).
    # The stern is roughly in the middle, but slightly off-center.
    
    # Since I don't have interactive crop, I'll try to rotate it first to align it vertically.
    # The lanterns are pointing right, so it needs a 90-degree counter-clockwise rotation.
    img_rotated = img.transpose(Image.ROTATE_90)
    width, height = img_rotated.size
    
    # In the rotated image (3000x4000):
    # The stern decoration area is roughly:
    # x: 500 to 2500
    # y: 500 to 3500
    # Let's try a conservative crop for the central decoration.
    
    # Coordinates (left, top, right, bottom)
    # The stern seems to occupy the central 2/3rds of the image height and width.
    left = 400
    top = 1000
    right = 2600
    bottom = 3000
    
    crop_img = img_rotated.crop((left, top, right, bottom))
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    crop_img.save(output_path)
    print(f"Successfully saved stern texture to {output_path}")

if __name__ == "__main__":
    input_img = "1665/7-provinces/20250821_115239.jpg"
    output_img = "1665/7-provinces/images/textures/stern_decoration.png"
    extract_stern_texture(input_img, output_img)
