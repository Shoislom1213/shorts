import time
from models.download.download import download_video
from logger import setup_logger

logger = setup_logger("retry ")

def download_with_retry(url):
    for attempt in range(50):
        try:
            logger.info(f"Download attempt {attempt + 1}")

            clean_link = download_video(url)
            if not clean_link:
                raise Exception("Download returned no file")

            logger.info(f"Download successful: {clean_link}")
            return clean_link

        except Exception as e:
            wait_time = (attempt + 1) * 500  # seconds
            logger.error(f"Download failed: {e}")
            logger.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    logger.critical("Download failed after all retries")
    return None