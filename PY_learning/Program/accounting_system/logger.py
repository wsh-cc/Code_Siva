import logging
from os import path

logging.basicConfig(
    filename=path.join(path.dirname(path.abspath(__file__)), "accounting_system.log"),
    level=logging.INFO,
    # level=logging.WARNING,
    # level=logging.ERROR,
    
    format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
)
logger = logging.getLogger(__name__)