import requests
import os
import sys
from pathlib import Path

WEBHOOK_URL = 'WEBHOOK LITERAL URL'

def send_image(webhook_url, image_path, image_name):
    with open(image_path, 'rb') as image_file:
        files = {'file': (image_name, image_file)}
        response = requests.post(webhook_url, files=files)

        if response.status_code == 200:
            print(f"Image {image_name} sent successfully.")
        else:
            print(f"Error sending image {image_name}: {response.status_code} - {response.text}")

def get_images(folder_path=None):
    if folder_path is None:
        folder_path = Path.cwd()
    else:
        folder_path = Path(folder_path)

    return list(folder_path.glob('*.jpg')) + list(folder_path.glob('*.png')) + list(folder_path.glob('*.jpeg'))

if __name__ == "__main__":
    folder_path = sys.argv[1] if len(sys.argv) > 1 else None
    images = get_images(folder_path)

    for image_path in images:
        send_image(WEBHOOK_URL, image_path, image_path.name)
