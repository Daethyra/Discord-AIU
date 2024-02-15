import os
import time
import logging
import requests
from PIL import Image, UnidentifiedImageError
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import HTTPError, RequestException
from queue import Queue

# Configuration
WEBHOOK_URL = "https://discord.com/api/webhooks/<YOUR_WEBHOOK_ID>/YOUR_WEBHOOK_TOKEN>"
MAX_ALLOWED_WORKERS = 50
FOLDER_PATH = './images/'
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
    """
    A class to upload images to Discord via a webhook.

    Attributes:
        max_retries (int): Maximum number of retries for failed uploads.
        backoff_delay (int): Initial backoff delay for retries in seconds.
        metrics (dict): Dictionary to track the number of sent, failed, and retried images.
        failed_queue (Queue): A queue to hold the paths of images that failed to upload.
    """
    def __init__(self, max_retries: int = 2, backoff_delay: int = 5):
        """
        Initialize DiscordImageUploader.

        Parameters:
            max_retries (int): Maximum number of retries for failed uploads. Default is 2.
            backoff_delay (int): Initial backoff delay for retries in seconds. Default is 5.
        """
        self.max_retries = max_retries
        self.backoff_delay = backoff_delay
        self.metrics = {"sent": 0, "failed": 0, "retried": 0}
        self.failed_queue = Queue()
    
    def validate_image(self, image_path: str) -> None:
        """
        Validate the size and dimensions of the image.

        Parameters:
            image_path (str): Path to the image file.

        Raises:
            ValueError: If the image size or dimensions are invalid.
        """
        file_size = os.path.getsize(image_path)
        if file_size < MIN_IMAGE_SIZE or file_size > MAX_IMAGE_SIZE:
            raise ValueError(f"Invalid size for image {image_path}. Size: {file_size} bytes")
        
        with Image.open(image_path) as img:
            width, height = img.size
            if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
                raise ValueError(f"Invalid dimensions for image {image_path}. Dimensions: {width}x{height}")

    def send_image(self, image_path: str, session: requests.Session) -> str:
        """
        Upload an image to Discord and handle retries for failures.

        Parameters:
            image_path (str): Path to the image file.
            session (requests.Session): A requests session for sending the image.

        Returns:
            str: Status indicating whether the image was 'sent' or 'failed'.
        """
        retries = 0
        backoff = self.backoff_delay
        while retries < self.max_retries:
            try:
                self.validate_image(image_path)
                with open(image_path, 'rb') as img_file:
                    response = session.post(WEBHOOK_URL, files={'file': (os.path.basename(image_path), img_file)})
                    response.raise_for_status()
                    self.metrics["sent"] += 1
                    return "sent"
            except (HTTPError, RequestException, ValueError, UnidentifiedImageError) as e:
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
        """
        Resend images that failed during the initial upload.

        Parameters:
            session (requests.Session): A requests session for resending the images.
        """
        with ThreadPoolExecutor(max_workers=MAX_ALLOWED_WORKERS) as executor:
            futures = {executor.submit(self.send_image, img_path, session): img_path for img_path in list(self.failed_queue.queue)}
            for future in as_completed(futures):
                img_path = futures[future]
                try:
                    status = future.result()
                except Exception as e:
                    logger.error(f"Exception occurred while resending {img_path}: {e}")

    def upload_images(self) -> None:
        """
        Upload images to Discord by scanning the designated folder and validating each image.

        Handles concurrency for uploads and retries failed uploads.
        Logs information regarding the upload process.
        """
        if not os.path.exists(FOLDER_PATH):
            logger.error(f"Folder {FOLDER_PATH} does not exist.")
            return

        image_paths = [os.path.join(dirpath, filename) 
                    for dirpath, _, filenames in os.walk(FOLDER_PATH) 
                    for filename in filenames if filename.endswith(('.jpg', '.png', '.jpeg', '.gif', '.bmp'))]
        
        with requests.Session() as session:
            with ThreadPoolExecutor(max_workers=MAX_ALLOWED_WORKERS) as executor:
                futures = {executor.submit(self.send_image, img_path, session): img_path for img_path in image_paths}
                for i, future in enumerate(as_completed(futures), 1):
                    img_path = futures[future]
                    try:
                        status = future.result()
                    except Exception as e:
                        logger.error(f"Exception occurred while sending {img_path}: {e}")
                    
                    # Log metrics periodically
                    if i % 10 == 0:  # Adjust the frequency as needed
                        logger.info(f"Progress: {i}/{len(image_paths)} images processed.")
                        logger.info(f"Current Metrics: {self.metrics}")
        
            logger.info("Final Metrics:")
            logger.info(self.metrics)
            self.resend_failed_images(session)

# Main Execution
if __name__ == '__main__':
    uploader = DiscordImageUploader()
    uploader.upload_images()
