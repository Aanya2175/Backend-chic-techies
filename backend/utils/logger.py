import logging

# Configure logging with proper format
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s %(levelname)s %(message)s"
)

# Use descriptive logger name
app_logger = logging.getLogger("backend_app")
