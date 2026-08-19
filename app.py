# app.py
import os
import logging
from flask import Flask, request, jsonify, render_template
from celery.exceptions import CeleryError

# Import your Celery tasks
from tasks import process_transaction, app as celery_app

# --- Configuration ---
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
FLASK_RUN_PORT = int(os.getenv('FLASK_RUN_PORT', 5000))

# --- Flask App Initialization ---
# In development, the React dev server handles the frontend. Flask is just an API.
app = Flask(__name__)
app.config['ENV'] = FLASK_ENV
app.config['DEBUG'] = FLASK_DEBUG

# --- Logging Setup ---
# Configure Flask's logger to use the same setup as tasks.py
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set Flask's default logger to our configured logger
app.logger.handlers = logger.handlers
app.logger.setLevel(logger.level)

@app.route('/health', methods=['GET'])
def health_check():
    """
    A simple health check endpoint to verify the application is running.
    """
    app.logger.info("Health check requested.")
    return jsonify({"status": "healthy", "environment": FLASK_ENV}), 200

@app.route('/transactions', methods=['POST'])
def create_transaction():
    """
    Receives transaction data and dispatches it to the Celery worker for asynchronous processing.
    """
    if not request.is_json:
        app.logger.warning("Received non-JSON request to /transactions.")
        return jsonify({"error": "Request must be JSON"}), 400

    transaction_data = request.get_json()
    app.logger.info(f"Received transaction data: {transaction_data}")

    # Basic input validation (more comprehensive validation should be done with a library like Marshmallow or Pydantic)
    required_fields = ['customer_id', 'amount', 'description']
    if not all(field in transaction_data for field in required_fields):
        missing_fields = [field for field in required_fields if field not in transaction_data]
        app.logger.error(f"Missing required fields in transaction data: {missing_fields}")
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    try:
        # Dispatch the task to Celery. .delay() is a shortcut for .apply_async()
        task = process_transaction.delay(transaction_data)
        app.logger.info(f"Transaction task {task.id} dispatched for customer {transaction_data.get('customer_id')}.")
        return jsonify({
            "message": "Transaction processing initiated",
            "task_id": task.id,
            "status_url": f"/tasks/{task.id}"
        }), 202 # 202 Accepted: The request has been accepted for processing, but the processing has not been completed.

    except CeleryError as e:
        app.logger.critical(f"Failed to dispatch Celery task: {e}", exc_info=True)
        return jsonify({"error": "Failed to queue transaction for processing. Please try again later."}), 500
    except Exception as e:
        app.logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route('/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    Retrieves the status of a Celery task.
    """
    task = celery_app.AsyncResult(task_id)
    response = {
        'state': task.state,
        'info': task.info, # Can contain progress or result
    }
    if task.state == 'FAILURE':
        response['error'] = str(task.info) # The exception instance
    return jsonify(response)

@app.errorhandler(404)
def not_found_error(error):
    """Handles 404 Not Found errors."""
    app.logger.warning(f"404 Not Found: {request.path}")
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handles 500 Internal Server Errors."""
    app.logger.error(f"500 Internal Server Error: {error}", exc_info=True)
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.logger.info(f"Starting Flask app in {FLASK_ENV} mode on port {FLASK_RUN_PORT}...")
    # In a production environment, use a WSGI server like Gunicorn or uWSGI.
    # For development, app.run() is fine.
    app.run(host='0.0.0.0', port=FLASK_RUN_PORT)