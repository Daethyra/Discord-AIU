import os
import time
import logging
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import threading

# Setup Logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] - %(message)s",
                    handlers=[logging.StreamHandler(), logging.FileHandler('image_uploader.log')])
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(".env")

# Configuration loaded from .env
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 2))
MAX_ALLOWED_WORKERS = int(os.getenv("MAX_ALLOWED_WORKERS", 50))
INITIAL_BACKOFF_DELAY = int(os.getenv("INITIAL_BACKOFF_DELAY", 5))
FOLDER_PATH = os.getenv("FOLDER_PATH", 'images/')
MIN_IMAGE_SIZE = int(os.getenv("MIN_IMAGE_SIZE", 5000))
MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", 20000000))
MIN_IMAGE_WIDTH = int(os.getenv("MIN_IMAGE_WIDTH", 256))
MIN_IMAGE_HEIGHT = int(os.getenv("MIN_IMAGE_HEIGHT", 256))

class ImageValidationError(Exception):
    """Custom exception for image validation errors."""
    pass

class FolderNotFoundError(Exception):
    """Custom exception for missing folder."""
    pass

class MetricsCollector:
    """Class to collect metrics related to image processing."""
    
    def __init__(self):
        self.metrics = {"sent": 0, "skipped": 0, "failed": 0, "retried": 0}

    def update_metrics(self, status: str) -> None:
        """Update the metrics based on the processing status."""
        if status in self.metrics:
            self.metrics[status] += 1

class ImageSender:
    """Class responsible for validating and sending images to a webhook."""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.metrics_collector = MetricsCollector()
        self.webhook_locks = {}

    def get_lock_for_webhook(self, webhook_url: str) -> threading.Lock:
        """Get a unique lock for a given webhook."""
        if webhook_url not in self.webhook_locks:
            self.webhook_locks[webhook_url] = threading.Lock()
        return self.webhook_locks[webhook_url]

    def validate_image_size(self, image_path: str) -> None:
        """Validate the size of the image."""
        file_size = os.path.getsize(image_path)
        if file_size < MIN_IMAGE_SIZE or file_size > MAX_IMAGE_SIZE:
            raise ImageValidationError(f"Invalid size for image {image_path}. Size: {file_size} bytes")

    def validate_image_dimensions(self, image_path: str) -> None:
        """Validate the dimensions of the image."""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
                    raise ImageValidationError(f"Invalid dimensions for image {image_path}. Dimensions: {width}x{height}")
        except UnidentifiedImageError:
            raise ImageValidationError(f"Corrupted or unsupported image format for {image_path}")

    def send_image_request(self, image_path: str) -> float:
        """Send the image to the webhook and return the retry delay if required."""
        retry_after = INITIAL_BACKOFF_DELAY
        try:
            with open(image_path, 'rb') as img_file, self.get_lock_for_webhook(self.webhook_url):
                response = requests.post(self.webhook_url, files={'image': img_file})
            
            response.raise_for_status()
            
            # Check rate limits
            remaining_requests = int(response.headers.get('X-RateLimit-Remaining', 1))
            if remaining_requests == 0:
                retry_after = int(response.headers.get('Retry-After', INITIAL_BACKOFF_DELAY))
            
            return retry_after
        except requests.RequestException as e:
            logger.error(f"Error sending image {image_path}. Error: {e}")
            return retry_after

    def send_image(self, image_path: str) -> str:
        """Validate, send, and handle retries for the image."""
        try:
            self.validate_image_size(image_path)
            self.validate_image_dimensions(image_path)
            retries = 0
            while retries < MAX_RETRIES:
                retry_after = self.send_image_request(image_path)
                if retry_after == 0:
                    self.metrics_collector.update_metrics("sent")
                    return "sent"
                else:
                    self.metrics_collector.update_metrics("retried")
                    time.sleep(retry_after)
                    retry_after *= 2
                retries += 1
        except ImageValidationError:
            self.metrics_collector.update_metrics("failed")
            return "failed"

def get_images(folder_path: str) -> list[str]:
    """Retrieve all valid image paths from the specified folder."""
    if not os.path.exists(folder_path):
        raise FolderNotFoundError(f"Folder {folder_path} does not exist.")
    return [os.path.join(dirpath, filename) for dirpath, _, filenames in os.walk(folder_path) for filename in filenames if filename.endswith(('.jpg', '.png', '.jpeg', '.gif', '.bmp'))]

if __name__ == '__main__':
    try:
        image_paths = get_images(FOLDER_PATH)
        MAX_WORKERS = min(MAX_ALLOWED_WORKERS, len(image_paths) // 10)
        image_sender = ImageSender(WEBHOOK_URL)

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(image_sender.send_image, img_path): img_path for img_path in image_paths}
            for future in as_completed(futures):
                img_path = futures[future]
                try:
                    status = future.result()
                    if status == "failed":
                        logger.warning(f"Image {img_path} failed after maximum retries")
                except Exception as e:
                    logger.error(f"Exception occurred while sending {img_path}: {e}")

        logger.info(image_sender.metrics_collector.metrics)
    except FolderNotFoundError as e:
        logger.error(e)