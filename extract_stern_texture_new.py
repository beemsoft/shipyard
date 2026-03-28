from PIL import Image
import os

def extract_stern_from_screenshot(input_path, output_path):
    # Open the image
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    img = Image.open(input_path)

    # In 'Screenshot 2026-03-27 210338.png' (883x776):
    # The image is rotated 90 degrees clockwise (the stern top is facing left).
    # Rotate it back to vertical.
    img_rotated = img.transpose(Image.ROTATE_90)
    # Now it's 776 x 883.
    # The stern is centered.
    # Dimensions for the crop (left, top, right, bottom):
    # The central decoration area with the lions and shield.

    left = 50
    top = 100
    right = 726
    bottom = 800

    crop_img = img_rotated.crop((left, top, right, bottom))

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    crop_img.save(output_path)
    print(f"Successfully saved stern texture to {output_path}")

if __name__ == "__main__":
    input_img = r"C:\Users\hpbee\IdeaProjects\Blender\shipyard\1665\7-provinces\Screenshot 2026-03-27 210338.png"
    output_img = r"C:\Users\hpbee\IdeaProjects\Blender\shipyard\1665\7-provinces\images\textures\stern_transom_texture.png"
    extract_stern_from_screenshot(input_img, output_img)
