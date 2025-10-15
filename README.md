# Discord Image Uploader

## Brief Description

`Discord Image Uploader` is an efficient Python module designed to upload images to Discord via a webhook. The module ensures image validation, robust error handling, and implements efficient request streaming and concurrent retries for failed uploads.

## Installation Guide

To use the script, clone the repository or download and unpack the latest release, the run:
`python src/discord_aiu.py --webhook_url <your webhook>`

You may also change the hardcoded webhook URL in the script itself.

## Contribution Guide

To contribute, install `Discord Image Uploader`, use PDM (Python Development Master):

1. **Install PDM**:
   - Follow the installation instructions [here](https://pdm.fming.dev/latest/, "Official Site").
   
2. **Clone the Repository**:
   - Clone the `Discord Image Uploader` repository to your local machine.

3. **Install Dependencies**:
   - Navigate to the repository's root directory and run:

     ```sh
     pdm install
     ```

## How to Use the Module

1. **Configure Webhook URL**:
   - Replace `YOUR_WEBHOOK_URL_HERE` in `WEBHOOK_URL` with your Discord webhook URL.

2. **Place Images**:
   - Place images in `./images/` directory.

3. **Run the Module**:
   - Execute `pdm run ./src/discord_aiu.py`. The module will validate and upload the images, logging the process.

4. **Check Logs**:
   - Review `image_uploader.log` for logs and metrics related to the uploads.

---

## Features

- **Request Streaming**: Utilizes `requests.Session` for efficient connection handling.

- **Session Reuse**: The same session is used for resending failed images, ensuring connection reuse.

- **Concurrent Retries**: Failed images are retried concurrently using `ThreadPoolExecutor`.

- **Image Validation**: Validates image size and dimensions before upload.

- **Error Handling**: Appropriately logs errors.

- **Periodic Metrics Logging**: Logs metrics periodically during the upload process.

---

##### ***[Click here for the outdated, yet stable version: Release v1.2](https://github.com/Daethyra/Webhook-Automation/releases/tag/v1.2, "Direct link")***

## License
This project is licensed under the GNU Affero General Public License (APL).
