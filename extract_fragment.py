from PIL import Image
import os

# Open the image
img_path = r'1666\7-provinces\20250821_115101.jpg'
img = Image.open(img_path)

# Image size is (4000, 3000)
# Schematic board is roughly in the center-bottom
# Let's try to crop the board.
# Estimates (x1, y1, x2, y2):
# x: from ~900 to ~3250
# y: from ~350 to ~2850
# Actually, the board occupies a large portion. Let's try:
# Left: 23% of width -> 920
# Right: 81% of width -> 3240
# Top: 36% of height -> 1080
# Bottom: 94% of height -> 2820

crop_box = (920, 1080, 3240, 2820)
fragment = img.crop(crop_box)

# Save the fragment
output_path = r'1666\7-provinces\images\schematic_fragment.png'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
fragment.save(output_path)

print(f"Fragment saved to: {output_path}")
