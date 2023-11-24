import requests
from bs4 import BeautifulSoup
import os
import tarfile

def download_file(url, save_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

def download_and_extract(url, save_directory):
    # Create the save directory if it doesn't exist
    os.makedirs(save_directory, exist_ok=True)

    # Download the .tgz file
    response = requests.get(url)
    response.raise_for_status()

    # Save the .tgz file
    save_path = os.path.join(save_directory, os.path.basename(url))
    with open(save_path, 'wb') as file:
        file.write(response.content)

    print(f'Downloaded successfully, Extracting the files!!!')

    # Extract the contents of the .tgz file
    with tarfile.open(save_path, 'r:gz') as tar:
        tar.extractall(save_directory)
    print("Extracting completed")

    # Remove the .tgz file
    os.remove(save_path)


# URL of the YCB objects website
base_url = 'http://ycb-benchmarks.s3-website-us-east-1.amazonaws.com/'

# Directory where you want to save the downloaded objects
PARENT_DIR = os.path.normpath(os.getcwd())
save_directory = os.path.join(PARENT_DIR,'blender_files/models/ycb_models/')

# Fetch the HTML content of the website
response = requests.get(base_url)
response.raise_for_status()

# Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')
links = soup.find_all('a')

objects_to_download = ['052_extra_large_clamp','035_power_drill','021_bleach_cleanser','024_bowl','005_tomato_soup_can',
                        '025_mug','009_gelatin_box','008_pudding_box','007_tuna_fish_can','011_banana','006_mustard_bottle',
                        '004_sugar_box','019_pitcher_base','002_master_chef_can','003_cracker_box','010_potted_meat_can',
                        '036_wood_block','037_scissors','040_large_marker','051_large_clamp','061_foam_brick'
                       ]

objects_to_download = [obj_name+'_google_16k' for obj_name in objects_to_download]

object_ids = []
for link in links:
    href = link.get('href')
    if href.endswith('google_16k.tgz'):
        object_id = href.split('/')[-1].split('.')[0]
        if object_id in objects_to_download:
            object_url = base_url+ href
            object_ids.append(object_url)

print("\n ******************************************************************** ")
print("PATH for saving the models : ", save_directory)
print("Number of objects to download : ", len(object_ids))
try:
    user_input = input("\nEnter \"y\" to continue rendering or \"n\" to abort the process: ").strip().lower()

    if user_input == "y":
        for idx,object_url in enumerate(object_ids):
            # Download and extract the .tgz file
            print(f'Downloading the object : {idx}/{len(object_ids)} .....')
            download_and_extract(object_url, save_directory)

        print('All objects downloaded.')
    else:
        print("Aborted the process.")

except KeyboardInterrupt:
    print("\nProcess aborted by user (Ctrl+C).")

print("\n ******************************************************************** ")
