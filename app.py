import os
from __init__ import create_app
import logging
app = create_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG
    app.logger.setLevel(logging.DEBUG)  # Ensure Flask logs debug messages

    app.logger.info("This is an info log")
    app.logger.debug("This is a debug log")
    app.logger.error("This is an error log")
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5328)))

