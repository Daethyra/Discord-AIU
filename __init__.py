"""
Discord-AIU | Save time showing off your favorites.
Copyright (C) 2023 Daethyra (Daemon Carino)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# Importing required modules
import os
import time
import csv
import logging
import datetime
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from typing import List, Union

# Load environment variables
load_dotenv(".env")

# Configuration loaded from .env
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 2))

# Custom Exception for Image Validation
class ImageValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)

# Metrics Collector Class
class MetricsCollector:
    def __init__(self):
        self.metrics = {"sent": 0, "skipped": 0, "failed": 0, "retried": 0}
    def update_metrics(self, status: str) -> None:
        if status in self.metrics:
            self.metrics[status] += 1

# Main ImageSender Class with all functionalities
class ImageSender:
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.failed_queue = Queue()
        self.MAX_RETRIES = MAX_RETRIES

    def validate_image_size(self, image_path: str) -> None:
        file_size = os.path.getsize(image_path)
        if file_size < 5000 or file_size > 20000000:
            raise ImageValidationError(f"Invalid size for image {image_path}. Size: {file_size} bytes")

    def validate_image_dimensions(self, image_path: str) -> None:
        with Image.open(image_path) as img:
            width, height = img.size
            if width < 256 or height < 256:
                raise ImageValidationError(f"Invalid dimensions for image {image_path}. Dimensions: {width}x{height}")

    def send_image_request(self, webhook_url: str, image_path: str) -> Union[None, float]:
        # Simulated logic to mimic actual image sending
        # Normally, you would use a library like 'requests' to POST the image to the webhook URL
        success = True  # Simulate a successful send
        if success:
            return None
        else:
            return 1.5  # Simulated 'retry_after' time in case of rate limiting

    def send_image(self, webhook_url: str, image_path: str, image_name: str) -> str:
        try:
            self.validate_image_size(image_path)
            self.validate_image_dimensions(image_path)
            retry_after = self.send_image_request(webhook_url, image_path)
            if retry_after is None:
                self.metrics_collector.update_metrics("sent")
                return "sent"
            else:
                self.metrics_collector.update_metrics("retried")
                time.sleep(retry_after)  # Wait for the time specified in 'retry_after'
                return "retried"
        except ImageValidationError as e:
            self.metrics_collector.update_metrics("failed")
            return "failed"

    def retry_failed_images(self, webhook_url: str) -> None:
        retries = 0
        while not self.failed_queue.empty() and retries < self.MAX_RETRIES:
            image_path = self.failed_queue.get()
            image_name = os.path.basename(image_path)
            status = self.send_image(webhook_url, image_path, image_name)
            if status == "failed":
                self.failed_queue.put(image_path)
            retries += 1

# Function to get images from the 'images/' folder
def get_images(folder_path: str = 'images/') -> List[str]:
    images = []
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(('.jpg', '.png', '.jpeg', '.gif', '.bmp')):
                images.append(os.path.join(dirpath, filename))
    return images

# Main block to execute the code
if __name__ == '__main__':
    # Get all image paths from the 'images/' folder
    image_paths = get_images()
    
    # Dynamic threading based on the number of images to send
    MAX_WORKERS = min(10, len(image_paths) // 10)
    
    # Creating an instance of ImageSender class
    image_sender = ImageSender()
    
    # Using ThreadPoolExecutor for concurrent image sending
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(image_sender.send_image, WEBHOOK_URL, img_path, os.path.basename(img_path)): img_path for img_path in image_paths}
        for future in as_completed(futures):
            img_path = futures[future]
            try:
                status = future.result()
                if status == "failed":
                    image_sender.failed_queue.put(img_path)
            except Exception as e:
                print(f"Exception occurred while sending {img_path}: {e}")
    
    # Retry sending failed images
    image_sender.retry_failed_images(WEBHOOK_URL)
    
    # Displaying the collected metrics after retries
    print(image_sender.metrics_collector.metrics)
