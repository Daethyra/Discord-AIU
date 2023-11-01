import os
import time
import logging
import requests
from PIL import Image, UnidentifiedImageError
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import HTTPError
from queue import Queue

# Configuration
WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"
MAX_ALLOWED_WORKERS = 50
FOLDER_PATH = 'images/'
MIN_IMAGE_SIZE = 5000
MAX_IMAGE_SIZE = 20000000
MIN_IMAGE_WIDTH = 256
MIN_IMAGE_HEIGHT = 256

# Setup Logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] - %(message)s",
                    handlers=[logging.StreamHandler(), logging.FileHandler('image_uploader.log')])
logger = logging.getLogger(__name__)

# DiscordImageUploader Class
class DiscordImageUploader:
    """A class to upload images to Discord via a webhook."""

    def __init__(self, max_retries: int = 2, backoff_delay: int = 5):
        """
        Initialize DiscordImageUploader.

        Parameters:
            max_retries: Maximum number of retries for failed uploads.
            backoff_delay: Initial backoff delay for retries.
        """
        self.max_retries = max_retries
        self.backoff_delay = backoff_delay
        self.metrics = {"sent": 0, "failed": 0, "retried": 0}
        self.failed_queue = Queue()
    
    def validate_image_size(self, image_path: str) -> None:
        """Validate the size of the image."""
        file_size = os.path.getsize(image_path)
        if file_size < MIN_IMAGE_SIZE or file_size > MAX_IMAGE_SIZE:
            raise ValueError(f"Invalid size for image {image_path}. Size: {file_size} bytes")
    
    def validate_image_dimensions(self, image_path: str) -> None:
        """Validate the dimensions of the image."""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
                    raise ValueError(f"Invalid dimensions for image {image_path}. Dimensions: {width}x{height}")
        except UnidentifiedImageError:
            raise ValueError(f"Corrupted or unsupported image format for {image_path}")

    def send_image(self, image_path: str, session: requests.Session) -> str:
        """Send an image to Discord via a webhook."""
        retries = 0
        backoff = self.backoff_delay

        with open(image_path, 'rb') as img_file:
            while retries < self.max_retries:
                try:
                    self.validate_image_size(image_path)
                    self.validate_image_dimensions(image_path)
                    response = session.post(WEBHOOK_URL, files={'image': img_file})
                    response.raise_for_status()
                    logger.info(f"Successfully sent {image_path}")
                    self.metrics["sent"] += 1
                    return "sent"
                except (HTTPError, ValueError) as e:
                    logger.warning(f"Failed to send {image_path}: {e}")
                    self.metrics["retried"] += 1
                    time.sleep(backoff)
                    retries += 1
                    backoff *= 2  # Exponential back-off
                
        logger.warning(f"Image {image_path} failed after maximum retries")
        self.metrics["failed"] += 1
        self.failed_queue.put(image_path)
        return "failed"
    
    def resend_failed_images(self, session: requests.Session) -> None:
        """Resend the failed images."""
        while not self.failed_queue.empty():
            image_path = self.failed_queue.get()
            status = self.send_image(image_path, session)
            if status == "failed":
                self.failed_queue.put(image_path)
            time.sleep(self.backoff_delay)
    
    def upload_images(self) -> None:
        """Upload images to Discord."""
        if not os.path.exists(FOLDER_PATH):
            logger.error(f"Folder {FOLDER_PATH} does not exist.")
            return

        image_paths = [os.path.join(dirpath, filename) 
                       for dirpath, _, filenames in os.walk(FOLDER_PATH) 
                       for filename in filenames if filename.endswith(('.jpg', '.png', '.jpeg', '.gif', '.bmp'))]
        
        with requests.Session() as session, ThreadPoolExecutor(max_workers=MAX_ALLOWED_WORKERS) as executor:
            futures = {executor.submit(self.send_image, img_path, session): img_path for img_path in image_paths}
            for future in as_completed(futures):
                img_path = futures[future]
                try:
                    status = future.result()
                except Exception as e:
                    logger.error(f"Exception occurred while sending {img_path}: {e}")
        
        logger.info(self.metrics)
        self.resend_failed_images(session)

# Main Execution
if __name__ == '__main__':
    uploader = DiscordImageUploader()
    uploader.upload_images()