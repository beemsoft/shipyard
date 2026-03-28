import requests
import os

texture_name = 'old_planks_02'
resolution = '2k' # Using 2k for better quality while being efficient
file_format = 'jpg'

# Base URLs for Poly Haven maps
maps = {
    'diffuse': f'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/{resolution}/{texture_name}/{texture_name}_diff_{resolution}.{file_format}',
    'nor_gl': f'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/{resolution}/{texture_name}/{texture_name}_nor_gl_{resolution}.{file_format}',
    'rough': f'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/{resolution}/{texture_name}/{texture_name}_rough_{resolution}.{file_format}',
    'disp': f'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/{resolution}/{texture_name}/{texture_name}_disp_{resolution}.{file_format}'
}

output_dir = os.path.join('1665', '7-provinces', 'images', 'textures', texture_name)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for map_type, url in maps.items():
    print(f"Downloading {texture_name} {map_type} {resolution}...")
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            filename = f"{texture_name}_{map_type}_{resolution}.{file_format}"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            print(f"Saved to {filepath}")
        else:
            print(f"Failed to download {map_type}: {r.status_code}")
    except Exception as e:
        print(f"Error downloading {map_type}: {e}")
