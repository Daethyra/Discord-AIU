import csv
import os
import sys
import logging
import datetime
from pathlib import Path
from typing import List
from time import sleep
from PIL import Image, UnidentifiedImageError
from dotenv import load_dotenv
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore

# Load environment variables
load_dotenv()

WEBHOOK_URL = os.getenv('WEBHOOK_URL')
RATE_LIMIT = float(os.getenv('RATE_LIMIT', 10))  # RATE_LIMIT in seconds
RETRY_COUNT = int(os.getenv('RETRY_COUNT', 2))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 5))
BACKOFF_BASE = int(os.getenv('BACKOFF_BASE', 15))  # Base delay for exponential backoff in seconds
BACKOFF_CAP = int(os.getenv('BACKOFF_CAP', 30))  # Maximum delay for exponential backoff in seconds
COOLDOWN_TIME = float(os.getenv('COOLDOWN_TIME', 15))  # Time to wait if being rate limited - (429 error)
MIN_FILE_SIZE = int(os.getenv('MIN_FILE_SIZE', 0)) # in bytes
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 20000000)) # in bytes, 20000000 bytes = 20 MB
MIN_WIDTH = int(os.getenv('MIN_WIDTH', 256)) # in pixels
MIN_HEIGHT = int(os.getenv('MIN_HEIGHT', 256)) # in pixels
COMPRESS_IMAGES = os.getenv('COMPRESS_IMAGES', 'NO')  # YES to compress images, NO to keep original quality
MAX_WORKERS = int(os.getenv('MAX_WORKERS', 2))  # Default to 2 if not set
SEMAPHORE_VALUE = int(os.getenv('SEMAPHORE_VALUE', 1))  # Default to 1 if not set

# Setup logging
current_time = datetime.datetime.now().strftime("%d-%m-%H-%M")
log_file = f'logs/upload_{current_time}.log'
LOG_FILE = f'logs/log_{current_time}.csv'
LOG_DIR = 'logs/'

# Ensure log directory exists
Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=log_file, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Create a session and a semaphore
session = requests.Session()
semaphore = Semaphore(SEMAPHORE_VALUE)

def compress_image(image_path: str) -> None:
    with Image.open(image_path) as img:
        img.save(image_path, optimize=True, quality=30)

def send_image(webhook_url: str, image_path: str, image_name: str) -> str:
    # Acquire the semaphore
    semaphore.acquire()
    try:
        file_size = os.path.getsize(image_path)
        if MAX_FILE_SIZE is not None and (file_size < MIN_FILE_SIZE or file_size > MAX_FILE_SIZE):
            logging.info(f"Skipping {image_name} due to file size {file_size}.")
            log_to_csv([image_name, 'Skipped', 'Size'])
            return "skipped"

        try:
            with Image.open(image_path) as img:
                width, height = img.size
                if width < MIN_WIDTH or height < MIN_HEIGHT:
                    logging.info(f"Skipping {image_name} due to dimensions {width}x{height}.")
                    log_to_csv([image_name, 'Skipped', 'Dimensions'])
                    return "skipped"
        except UnidentifiedImageError:
            logging.info(f"Skipping {image_name} due to UnidentifiedImageError.")
            log_to_csv([image_name, 'Skipped', 'UnidentifiedImageError'])
            return "skipped"

        if COMPRESS_IMAGES.upper() == 'YES':
            compress_image(image_path)

        for attempt in range(RETRY_COUNT):
            try:
                with open(image_path, 'rb') as image_file:
                    files = {'file': (image_name, image_file)}
                    response = session.post(webhook_url, files=files)

                    if response.status_code == 200:
                        logging.info(f"Image {image_name} sent successfully.")
                        log_to_csv([image_name, 'Sent', 'Success'])
                        return "sent"
                    elif response.status_code == 429:  # If rate limit error
                        retry_after = response.json().get('retry_after', COOLDOWN_TIME)
                        logging.error(f"Rate limit error sending image {image_name}: {response.status_code} - {response.text}")
                        sleep(retry_after)
                        continue
                    else:
                        logging.error(f"Error sending image {image_name}: {response.status_code} - {response.text}")
            except Exception as e:
                logging.error(f"Failed to send image {image_name}: {str(e)}")
            if attempt < RETRY_COUNT - 1:  # No need to sleep after the last attempt
                backoff_time = min(BACKOFF_BASE * (2 ** attempt), BACKOFF_CAP)
                logging.info(f"Sleeping for {backoff_time} seconds before next retry...")
                sleep(backoff_time)

        logging.error(f"Failed to send image {image_name} after {RETRY_COUNT} attempts.")
        log_to_csv([image_name, 'Failed', 'Retries'])
        return "failed"
    finally:
        # Release the semaphore
        semaphore.release()

def get_images(folder_path: str = None) -> List[Path]:
    if folder_path is None:
        folder_path = str(Path.cwd())
    images = []
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(('.jpg', '.png', '.jpeg', '.gif', '.bmp')):
                images.append(Path(dirpath, filename))
    return images

def log_to_csv(log_data: List[str]) -> None:
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(log_data)

def retry_failed(failed_images: List[Path]):
    if not failed_images:
        return

    print(f"Found {len(failed_images)} images that failed to send. Do you want to retry them? (yes/no)")
    answer = input().strip().lower()
    if answer == "yes":
        print("Retrying failed images...")
        for image_path in failed_images:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(send_image, WEBHOOK_URL, str(image_path), image_path.name)
                if future.result() == "sent":
                    print(f"Successfully resent {image_path.name}")
                    failed_images.remove(image_path)
                else:
                    print(f"Failed to resend {image_path.name}")
    else:
        print("Not retrying failed images.")

if __name__ == "__main__":
    folder_path = sys.argv[1] if len(sys.argv) > 1 else None
    images = get_images(folder_path)
    total_images = len(images)
    sent_images = 0
    skipped_images = 0
    failed_images = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(send_image, WEBHOOK_URL, str(image_path), image_path.name) for image_path in images]
        for i, future in enumerate(as_completed(futures)):
            status = future.result()
            if status == "sent":
                sent_images += 1
            elif status == "skipped":
                skipped_images += 1
            elif status == "failed":
                failed_images += 1

            logging.info(f"Progress: Sent {sent_images}, Skipped {skipped_images}, Failed {failed_images} of {total_images} images.")

    logging.info(f"Finished: Sent {sent_images}, Skipped {skipped_images}, Failed {failed_images} of {total_images} images.")

    # New code to retry failed images
    failed_images = [image_path for future, image_path in zip(futures, images) if future.result() == "failed"]
    retry_failed(failed_images)
