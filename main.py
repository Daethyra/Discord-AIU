import os
import sys
import logging
from pathlib import Path
from typing import List
from time import sleep
from PIL import Image
from dotenv import load_dotenv
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv()

WEBHOOK_URL = os.getenv('WEBHOOK_URL')
RETRY_COUNT = int(os.getenv('RETRY_COUNT', 3))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 5))
MIN_FILE_SIZE = int(os.getenv('MIN_FILE_SIZE', 0))
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 5000000))
MIN_WIDTH = int(os.getenv('MIN_WIDTH', 0))
MIN_HEIGHT = int(os.getenv('MIN_HEIGHT', 0))

# Setup logging
logging.basicConfig(level=logging.INFO)

def compress_image(image_path: str) -> None:
    with Image.open(image_path) as img:
        img.save(image_path, optimize=True, quality=85)

def send_image(webhook_url: str, image_path: str, image_name: str) -> None:
    # Check file size
    file_size = os.path.getsize(image_path)
    if file_size < MIN_FILE_SIZE or file_size > MAX_FILE_SIZE:
        logging.info(f"Skipping {image_name} due to file size {file_size}.")
        return

    # Check image dimensions
    with Image.open(image_path) as img:
        width, height = img.size
        if width < MIN_WIDTH or height < MIN_HEIGHT:
            logging.info(f"Skipping {image_name} due to dimensions {width}x{height}.")
            return

    # Compress image
    compress_image(image_path)

    # Send image
    for attempt in range(RETRY_COUNT):
        try:
            with open(image_path, 'rb') as image_file:
                files = {'file': (image_name, image_file)}
                response = requests.post(webhook_url, files=files)

                if response.status_code == 200:
                    logging.info(f"Image {image_name} sent successfully.")
                    return
                else:
                    logging.error(f"Error sending image {image_name}: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"Failed to send image {image_name}: {str(e)}")

        if attempt < RETRY_COUNT - 1:  # Don't delay after the last attempt
            sleep(RETRY_DELAY)

    logging.error(f"Failed to send image {image_name} after {RETRY_COUNT} attempts.")

def get_images(folder_path: str = None) -> List[Path]:
    if folder_path is None:
        folder_path = Path.cwd()
    else:
        folder_path = Path(folder_path)

    return list(folder_path.glob('*.jpg')) + list(folder_path.glob('*.png')) + list(folder_path.glob('*.jpeg')) + list(folder_path.glob('*.gif')) + list(folder_path.glob('*.bmp'))

if __name__ == "__main__":
    folder_path = sys.argv[1] if len(sys.argv) > 1 else None
    images = get_images(folder_path)
    total_images = len(images)
    sent_images = 0

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(send_image, WEBHOOK_URL, image_path, image_path.name) for image_path in images]

        for future in as_completed(futures):
            if future.exception() is None:
                sent_images += 1
                logging.info(f"Progress: Sent {sent_images} of {total_images} images.")

    logging.info(f"Finished: Sent {sent_images} of {total_images} images.")
