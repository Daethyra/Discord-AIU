# Multi-Hooker 🎣

Previously known as Discord-Image-Webhook, Multi-Hooker is a versatile Python script that sends images to any number of Discord webhooks. It can work with images from a specified folder or even the current working directory. 

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

`git clone git@github.com:YourUsername/Multi-Hooker.git`

2. Install [Poetry](https://python-poetry.org/docs/#installation) if you haven't already.
3. Install the necessary libraries using Poetry. 
   
poetry install
   

## Usage 🚀

Define your actual Discord webhook URL and other settings in a .env file in the project's root directory.

To send images from the current working directory:

`python main.py`

To send images from a specified folder:

`python main.py /path/to/your/folder`


Enjoy the future of image sharing with Multi-Hooker! 🎈

## License
This project is licensed under the terms of the [GNU_AGPL-License](./LICENSE).
