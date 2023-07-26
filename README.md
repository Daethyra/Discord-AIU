# Discord-Image-Webhook

This Python script sends images to a specified Discord webhook. The script can be used to send images from a given folder or the current working directory.

## Features

- Send images with .jpg, .jpeg, and .png file extensions.
- Specify a folder path or use the current working directory.
- Images are sent one by one to the specified webhook URL as normal messages.

## Requirements

- Python 3.10 or higher
- `requests` library

## Installation

1. Clone the repository or download the script.
   `git clone git@github.com:Daethyra/Discord-Image-Webhook.git`
2. Install the `requests` library.
   `pip install requests`

## Usage

Replace the `WEBHOOK_URL` in the script with your actual Discord webhook URL.

### To send images from the current working directory:

* `python main.py`

### To send images from a specified folder:

* `python main.py /path/to/your/folder`
