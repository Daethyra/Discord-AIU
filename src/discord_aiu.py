import os
import time
import logging
import argparse
import random
import argparse
import random
import requests
from PIL import Image, UnidentifiedImageError
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import HTTPError, RequestException
from queue import Queue


# Set your webhook URL here if you don't want to pass it as argument every time
# Leave as None to require --webhook-url argument
HARDCODED_WEBHOOK_URL = None  # or set to "https://discord.com/api/webhooks/..."

# Default folder for images (can be overridden by --folder argument)
DEFAULT_FOLDER_PATH = './images/'

def setup_logging():
    """Setup proper logging to both file and stdout with consistent behavior"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")
    
    # File handler - ensures all logs go to file
    file_handler = logging.FileHandler('image_uploader.log', mode='a', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Stream handler - ensures all logs go to stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    
    # Add both handlers
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger

# Initialize logging
logger = setup_logging()

class DiscordImageUploader:
    """
    A production-grade class to upload images to Discord via webhook.
    Supports individual images, folders, and random selection.
    """
    def __init__(self, webhook_url: str, max_workers: int = 3,
                 min_image_size: int = 2000, max_image_size: int = 20000000,
                 min_image_width: int = 32, min_image_height: int = 32,
                 max_retries: int = 2, backoff_delay: int = 10):
        """
        Initialize DiscordImageUploader with configurable parameters.
        
        Initialize DiscordImageUploader with configurable parameters.
        
        Parameters:
            webhook_url (str): Discord webhook URL (required)
            max_workers (int): Maximum concurrent workers (default: 3)
            min_image_size (int): Minimum image size in bytes (default: 2000)
            max_image_size (int): Maximum image size in bytes (default: 20000000)
            min_image_width (int): Minimum image width in pixels (default: 32)
            min_image_height (int): Minimum image height in pixels (default: 32)
            max_retries (int): Maximum retry attempts (default: 2)
            backoff_delay (int): Initial backoff delay in seconds (default: 10)
        """
        self.webhook_url = webhook_url
        self.max_workers = max_workers
        self.min_image_size = min_image_size
        self.max_image_size = max_image_size
        self.min_image_width = min_image_width
        self.min_image_height = min_image_height
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
            UnidentifiedImageError: If the image cannot be opened.
            UnidentifiedImageError: If the image cannot be opened.
        """
        if not os.path.exists(image_path):
            raise ValueError(f"Image file does not exist: {image_path}")
            
        if not os.path.exists(image_path):
            raise ValueError(f"Image file does not exist: {image_path}")
            
        file_size = os.path.getsize(image_path)
        if file_size < self.min_image_size:
            raise ValueError(f"Image too small: {image_path} ({file_size} bytes < {self.min_image_size} bytes)")
        if file_size > self.max_image_size:
            raise ValueError(f"Image too large: {image_path} ({file_size} bytes > {self.max_image_size} bytes)")
        if file_size < self.min_image_size:
            raise ValueError(f"Image too small: {image_path} ({file_size} bytes < {self.min_image_size} bytes)")
        if file_size > self.max_image_size:
            raise ValueError(f"Image too large: {image_path} ({file_size} bytes > {self.max_image_size} bytes)")
        
        with Image.open(image_path) as img:
            width, height = img.size
            if width < self.min_image_width or height < self.min_image_height:
                raise ValueError(f"Image dimensions too small: {image_path} ({width}x{height} < {self.min_image_width}x{self.min_image_height})")
            if width < self.min_image_width or height < self.min_image_height:
                raise ValueError(f"Image dimensions too small: {image_path} ({width}x{height} < {self.min_image_width}x{self.min_image_height})")

    def send_image(self, image_path: str, session: requests.Session) -> str:
        """
        Upload an image to Discord with retry logic.
        
        Upload an image to Discord with retry logic.
        
        Parameters:
            image_path (str): Path to the image file.
            session (requests.Session): Requests session for connection pooling.
            
            session (requests.Session): Requests session for connection pooling.
            
        Returns:
            str: Status indicating 'sent' or 'failed'
            str: Status indicating 'sent' or 'failed'
        """
        retries = 0
        current_backoff = self.backoff_delay
        
        while retries <= self.max_retries:
        current_backoff = self.backoff_delay
        
        while retries <= self.max_retries:
            try:
                self.validate_image(image_path)
                with open(image_path, 'rb') as img_file:
                    response = session.post(
                        self.webhook_url, 
                        files={'file': (os.path.basename(image_path), img_file)},
                        timeout=30
                    )
                    response = session.post(
                        self.webhook_url, 
                        files={'file': (os.path.basename(image_path), img_file)},
                        timeout=30
                    )
                    response.raise_for_status()
                    self.metrics["sent"] += 1
                    logger.info(f"✅ Successfully sent: {image_path}")
                    logger.info(f"✅ Successfully sent: {image_path}")
                    return "sent"
                    
                    
            except (HTTPError, RequestException, ValueError, UnidentifiedImageError) as e:
                logger.warning(f"⚠️ Attempt {retries + 1}/{self.max_retries + 1} failed for {image_path}: {e}")
                logger.warning(f"⚠️ Attempt {retries + 1}/{self.max_retries + 1} failed for {image_path}: {e}")
                self.metrics["retried"] += 1
                
                if retries == self.max_retries:
                    break
                    
                time.sleep(current_backoff)
                
                if retries == self.max_retries:
                    break
                    
                time.sleep(current_backoff)
                retries += 1
                current_backoff *= 2  # Exponential backoff
                current_backoff *= 2  # Exponential backoff
        
        logger.error(f"❌ Failed after {self.max_retries + 1} attempts: {image_path}")
        logger.error(f"❌ Failed after {self.max_retries + 1} attempts: {image_path}")
        self.metrics["failed"] += 1
        self.failed_queue.put(image_path)
        return "failed"
    
    def resend_failed_images(self, session: requests.Session) -> None:
        """Retry images that failed during initial upload."""
        if self.failed_queue.empty():
            return
            
        failed_count = self.failed_queue.qsize()
        logger.info(f"🔄 Retrying {failed_count} failed images...")
        
        with ThreadPoolExecutor(max_workers=min(self.max_workers, failed_count)) as executor:
            futures = {
                executor.submit(self.send_image, img_path, session): img_path 
                for img_path in list(self.failed_queue.queue)
            }
            
        """Retry images that failed during initial upload."""
        if self.failed_queue.empty():
            return
            
        failed_count = self.failed_queue.qsize()
        logger.info(f"🔄 Retrying {failed_count} failed images...")
        
        with ThreadPoolExecutor(max_workers=min(self.max_workers, failed_count)) as executor:
            futures = {
                executor.submit(self.send_image, img_path, session): img_path 
                for img_path in list(self.failed_queue.queue)
            }
            
            for future in as_completed(futures):
                img_path = futures[future]
                try:
                    future.result()
                    future.result()
                except Exception as e:
                    logger.error(f"💥 Critical error during retry of {img_path}: {e}")
                    logger.error(f"💥 Critical error during retry of {img_path}: {e}")

    def upload_images(self, image_paths: list) -> None:
    def upload_images(self, image_paths: list) -> None:
        """
        Upload multiple images with concurrent workers.
        
        Parameters:
            image_paths (list): List of image file paths to upload
        Upload multiple images with concurrent workers.
        
        Parameters:
            image_paths (list): List of image file paths to upload
        """
        if not image_paths:
            logger.error("❌ No images provided for upload")
        if not image_paths:
            logger.error("❌ No images provided for upload")
            return

        total_images = len(image_paths)
        logger.info(f"🚀 Starting upload of {total_images} images with {self.max_workers} workers")

        total_images = len(image_paths)
        logger.info(f"🚀 Starting upload of {total_images} images with {self.max_workers} workers")

        with requests.Session() as session:
            # Initial upload pass
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self.send_image, img_path, session): img_path 
                    for img_path in image_paths
                }
                
            # Initial upload pass
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self.send_image, img_path, session): img_path 
                    for img_path in image_paths
                }
                
                for i, future in enumerate(as_completed(futures), 1):
                    img_path = futures[future]
                    try:
                        future.result()
                        future.result()
                    except Exception as e:
                        logger.error(f"💥 Unexpected error with {img_path}: {e}")
                    
                    # Progress logging
                    if i % 10 == 0 or i == total_images:
                        logger.info(f"📊 Progress: {i}/{total_images} | Metrics: {self.metrics}")
            
            # Final metrics after initial pass
            logger.info(f"📈 Upload completed. Final metrics: {self.metrics}")
            
            # Retry failed images
            if not self.failed_queue.empty():
                self.resend_failed_images(session)
                logger.info(f"🎯 Final metrics after retries: {self.metrics}")

def find_images_in_folder(folder_path: str) -> list:
    """
    Recursively find all image files in a folder.
    
    Parameters:
        folder_path (str): Path to search for images
        
    Returns:
        list: List of absolute paths to image files
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder does not exist: {folder_path}")
    
    supported_formats = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    image_paths = []
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(supported_formats):
                image_paths.append(os.path.abspath(os.path.join(root, file)))
    
    logger.info(f"🔍 Found {len(image_paths)} images in {folder_path}")
    return image_paths

def select_random_image(image_paths: list) -> list:
    """
    Select a single random image from a list.
    
    Parameters:
        image_paths (list): List of image paths
        
    Returns:
        list: List containing one random image path
    """
    if not image_paths:
        raise ValueError("No images available for random selection")
    
    selected = random.choice(image_paths)
    logger.info(f"🎲 Randomly selected: {selected}")
    return [selected]

def main():
    """CLI entry point with robust argument parsing and backward compatibility."""
    parser = argparse.ArgumentParser(
        description='Production-grade Discord image uploader',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
Examples:
  # Backward compatible: Upload all images from default folder (if webhook is hardcoded)
  python script.py
  
  # Upload all images from default folder with CLI webhook
  python script.py --webhook-url "YOUR_WEBHOOK_URL"
  
  # Upload specific images
  python script.py --webhook-url "URL" image1.jpg image2.png
  
  # Upload from custom folder
  python script.py --webhook-url "URL" --folder "/path/to/images"
  
  # Send one random image from folder
  python script.py --webhook-url "URL" --random
  
  # Custom configuration
  python script.py --webhook-url "URL" --max-workers 10 --max-retries 3 --random
  
  # Legacy mode: Just run the script (requires HARDCODED_WEBHOOK_URL in script)
  python script.py
        '''
    )
    
    # Webhook URL argument (optional if hardcoded)
    parser.add_argument('--webhook-url', 
                       help='Discord webhook URL (optional if hardcoded in script)')
    
    # Operation mode arguments
    parser.add_argument('--folder', default=DEFAULT_FOLDER_PATH,
                       help=f'Folder to process images from (default: {DEFAULT_FOLDER_PATH})')
    parser.add_argument('--random', action='store_true',
                       help='Send a single random image from the folder or provided images')
    
    # Configuration arguments  
    parser.add_argument('--max-workers', type=int, default=3,
                       help='Maximum concurrent workers (default: 3)')
    parser.add_argument('--min-size', type=int, default=2000,
                       help='Minimum image size in bytes (default: 2000)')
    parser.add_argument('--max-size', type=int, default=20000000,
                       help='Maximum image size in bytes (default: 20000000)')
    parser.add_argument('--min-width', type=int, default=32,
                       help='Minimum image width in pixels (default: 32)')
    parser.add_argument('--min-height', type=int, default=32,
                       help='Minimum image height in pixels (default: 32)')
    parser.add_argument('--max-retries', type=int, default=2,
                       help='Maximum retry attempts (default: 2)')
    parser.add_argument('--backoff-delay', type=int, default=10,
                       help='Initial backoff delay in seconds (default: 10)')
    
    # Positional arguments for individual images
    parser.add_argument('images', nargs='*', 
                       help='Individual image files to upload')
    
    args = parser.parse_args()
    
    try:
        # Determine webhook URL (CLI argument takes precedence over hardcoded)
        webhook_url = args.webhook_url or HARDCODED_WEBHOOK_URL
        
        if not webhook_url:
            logger.error("❌ Webhook URL not provided. Either:")
            logger.error("   - Pass --webhook-url argument, OR")
            logger.error("   - Set HARDCODED_WEBHOOK_URL in the script")
            return 1
        
        if "YOUR_WEBHOOK" in webhook_url or "<YOUR_WEBHOOK" in webhook_url:
            logger.error("❌ Webhook URL appears to be unconfigured placeholder")
            logger.error("   Please set a valid webhook URL")
            return 1
        
        # Determine image source
        if args.images:
            # Use provided individual images
            image_paths = [os.path.abspath(img) for img in args.images]
            logger.info(f"📦 Processing {len(image_paths)} provided images")
        else:
            # Use folder scanning
            image_paths = find_images_in_folder(args.folder)
        
        # Apply random selection if requested
        if args.random:
            image_paths = select_random_image(image_paths)
        
        # Validate we have images to process
        if not image_paths:
            logger.error("❌ No valid images found to process")
            return 1
        
        # Initialize and run uploader
        uploader = DiscordImageUploader(
            webhook_url=webhook_url,
            max_workers=args.max_workers,
            min_image_size=args.min_size,
            max_image_size=args.max_size,
            min_image_width=args.min_width,
            min_image_height=args.min_height,
            max_retries=args.max_retries,
            backoff_delay=args.backoff_delay
        )
        
        uploader.upload_images(image_paths)
        return 0
        
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
    exit(main())