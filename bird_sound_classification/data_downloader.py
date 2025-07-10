import pandas as pd
import os
import requests
import xml.etree.ElementTree as ET
from collections import defaultdict
from urllib.parse import urlparse
from tqdm import tqdm

def get_audio_url(metadata_url):
    """Extract audio URL from metadata XML."""
    try:
        response = requests.get(metadata_url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            namespace = {'dwc': 'http://rs.tdwg.org/dwc/terms/'}
            audio_url = root.find('.//dwc:associatedMedia', namespace)
            if audio_url is not None:
                return audio_url.text
    except Exception as e:
        print(f"Failed to get audio URL from {metadata_url}: {e}")
    return None

# Read the metadata file
df = pd.read_csv('occurrence.txt', sep='\t', low_memory=False)

# Collect all audio URLs and corresponding bird names
audio_records = []
print("Extracting audio URLs...")
for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
    for col in ['references', 'associatedMedia']:
        if col in df.columns and pd.notna(row[col]):
            url = str(row[col]).strip()
            if url.lower().endswith(('.mp3', '.wav')):
                audio_records.append((url, row['scientificName']))
            else:
                # Assume it's a metadata URL; try to extract audio link
                audio_url = get_audio_url(url)
                if audio_url:
                    audio_records.append((audio_url, row['scientificName']))

# Group URLs by bird name
bird_to_urls = defaultdict(list)
for url, bird_name in audio_records:
    bird_to_urls[bird_name].append(url)

# Filter birds with at least 10 audio files (adjust as needed)
min_files = 10
birds_with_min_10 = {bird: urls for bird, urls in bird_to_urls.items() if len(urls) >= min_files}

# Base folder for all bird sounds
os.makedirs('bird_sounds', exist_ok=True)

print("Downloading audio files...")
for bird_name, urls in birds_with_min_10.items():
    # Clean bird name for folder
    folder_name = ''.join(c if c.isalnum() else '_' for c in bird_name)
    folder_path = os.path.join('bird_sounds', folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    # Download each audio file for this bird with progress bar
    for i, url in enumerate(tqdm(urls, desc=f"Downloading {bird_name}", leave=False)):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                # Get filename from URL or use generic name
                filename = os.path.basename(urlparse(url).path)
                if not filename.lower().endswith(('.mp3', '.wav')):
                    filename = f'audio_{i}.mp3'
                audio_path = os.path.join(folder_path, filename)
                with open(audio_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                # tqdm.write(f"Downloaded: {audio_path}")  # Optional: uncomment to print each file
        except Exception as e:
            tqdm.write(f"Failed to download {url}: {e}")

print("Download complete!")
