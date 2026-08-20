# app.py
import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from celery.exceptions import CeleryError

# Import your Celery tasks
from tasks import process_transaction, app as celery_app

# --- Configuration ---
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
FLASK_RUN_PORT = int(os.getenv('FLASK_RUN_PORT', 5000))

# Path to the built React app (created by `npm run build` inside the frontend dir)
REACT_BUILD_DIR = os.getenv('REACT_BUILD_DIR', os.path.join(os.path.dirname(__file__), 'build'))

# --- Flask App Initialization ---
app = Flask(__name__, static_folder=REACT_BUILD_DIR, static_url_path='')
app.config['ENV'] = FLASK_ENV
app.config['DEBUG'] = FLASK_DEBUG

# Allow the React dev server (localhost:3000) to hit this API directly,
# in addition to the CRA proxy. Safe to keep in production too.
CORS(app, resources={r"/transactions*": {"origins": "*"}, r"/tasks/*": {"origins": "*"}, r"/health": {"origins": "*"}})

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app.logger.handlers = logger.handlers
app.logger.setLevel(logger.level)


def _safe_task_info(task):
    """
    task.info can be a plain dict (progress/result) OR a raw Exception
    instance when the task failed. jsonify() cannot serialize an
    Exception, so normalize it to a JSON-safe value here.
    """
    info = task.info
    if isinstance(info, BaseException):
        return {"error": str(info), "type": type(info).__name__}
    if isinstance(info, (dict, list, str, int, float, bool)) or info is None:
        return info
    # Fallback for any other non-serializable object
    return str(info)


@app.route('/health', methods=['GET'])
def health_check():
    """A simple health check endpoint to verify the application is running."""
    app.logger.info("Health check requested.")
    return jsonify({"status": "healthy",