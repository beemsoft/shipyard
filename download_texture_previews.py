import requests
import os

urls = {
    'old_planks_02': 'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/old_planks_02/old_planks_02_diff_1k.jpg',
    'weathered_planks': 'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/weathered_planks/weathered_planks_diff_1k.jpg',
    'wood_planks': 'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/wood_planks/wood_planks_diff_1k.jpg',
    'worn_planks': 'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/worn_planks/worn_planks_diff_1k.jpg'
}

output_dir = r'1665\7-provinces\images\textures'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for name, url in urls.items():
    print(f"Downloading {name}...")
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            filepath = os.path.join(output_dir, f"{name}_preview.jpg")
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            print(f"Saved to {filepath}")
        else:
            print(f"Failed to download {name}: {r.status_code}")
    except Exception as e:
        print(f"Error downloading {name}: {e}")
