import logging
import os

def setup_logger(name="app", log_file="logs/app.log"):
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 🔁 duplicate handler bo‘lmasligi uchun
    if logger.hasHandlers():
        return logger

    # 📄 file handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # 🖥 console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 🎨 format
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S"
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger