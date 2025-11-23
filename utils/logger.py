import logging

def get_logger(file_name: str = "debug.log"):
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(file_name), logging.StreamHandler()],
    )
    logger = logging.getLogger()
    return logger