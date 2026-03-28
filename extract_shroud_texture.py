from PIL import Image
import os

def extract_shroud_texture(input_path, output_path):
    # Open the image
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    img = Image.open(input_path)
    
    # Image 20250821_115316.jpg is 4000x3000.
    # It's sideways (pointing right), so rotate 90 degrees CCW.
    img_rotated = img.transpose(Image.ROTATE_90)
    width, height = img_rotated.size
    
    # Coordinates (left, top, right, bottom)
    # The shrouds (standing rigging) are clearly visible here.
    # In the rotated image (3000x4000), this is roughly the top 1/3 of the area.
    left = 300
    top = 200
    right = 2700
    bottom = 1500
    
    crop_img = img_rotated.crop((left, top, right, bottom))
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    crop_img.save(output_path)
    print(f"Successfully saved shroud texture to {output_path} (Size: {crop_img.size})")

if __name__ == "__main__":
    input_img = "1665/7-provinces/20250821_115316.jpg"
    output_img = "1665/7-provinces/images/textures/shroud_texture.png"
    extract_shroud_texture(input_img, output_img)
