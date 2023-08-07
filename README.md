#### Please see ***[Release v1.2](https://github.com/Daethyra/Webhook-Automation/releases/tag/v1.2)*** for the Discord image uploader, an automated webhook interaction tool.

## Multi-Hooker
## Features 🌟

* **Support for Various Formats** 🖼️: Send images with .jpg, .jpeg, .png, .gif, and .bmp file extensions.
* **Choose Your Source** 📂: Specify a folder path or use the current working directory.
* **Environment Variables** 🌍: Configure with ease and security! All settings have been moved to environment variables.
* **Error Handling and Logging** 📝: Comprehensive error handling with automatic retry and rate limit handling. Plus, all logs are neatly saved in a CSV file for easy tracking.
* **Concurrency** 🚄: Experience a significant speed boost when sharing many images thanks to our concurrency feature.
* **Semaphore** 🚦: We've added a semaphore to ensure we don't overload servers. This is the first step towards enabling the use of multiple webhooks through LLM agents.
* **Image Validation and Compression** 🖼️: We now check your images for size and dimensions before sending. Plus, there's an optional image compression feature to reduce data usage.
* **Retry Failed Images** 🔁: If any images fail to send, don't worry! We've got a new retry option to ensure your images reach their destination.
* **Progress Report** 📊: Stay informed with our new progress report, detailing the number of images sent, skipped, and failed.

## Requirements 📌

* Python 3.10 or higher
* Poetry for dependency management

## Installation 🛠️

1. Clone the repository or download the script.

   - `git clone https://github.com/Daethyra/Multi-hooker.git`
2. Install [Poetry](https://python-poetry.org/docs/#installation) if you haven't already.

   - `pip install --no-cache-dir -r requirements.txt`
3. Install the necessary libraries using Poetry.

   - `poetry install`

## Usage 🚀

Define your actual Discord webhook URL and other settings in a .env file in the project's root directory.

To send images from the current working directory:

- `python main.py`

To send images from a specified folder:

- `python main.py /path/to/your/folder`

I hope you enjoy using Multi-Hooker! 🎈

## License

Multi-Hooker | LLM-Agent manager for webhook interactions and automated posting
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
along with this program.  If not, *[get one by clicking here.](https://www.gnu.org/licenses/)*

*This project is licensed under the terms of the [GNU_AGPL-License](./LICENSE).*
