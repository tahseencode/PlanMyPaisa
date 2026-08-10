# tasks.py
import os
import logging
from celery import Celery
from nessie_client import NessieClient
from typing import Dict, Any

# --- Configuration ---
# Load configuration from environment variables for flexibility and security.
# Provide sensible defaults for development, but ensure they are set in production.
REDIS_BROKER_URL = os.getenv('REDIS_BROKER_URL', 'redis://localhost:6379/0')
NESSIE_API_KEY = os.getenv('NESSIE_API_KEY', 'YOUR_NESSIE_API_KEY_DEFAULT') # IMPORTANT: Set this in your production environment!

# --- Logging Setup ---
# Configure a robust logging system instead of simple print statements.
# This allows for better monitoring, debugging, and log management.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Celery App Initialization ---
app = Celery('tasks', broker=REDIS_BROKER_URL)

# --- Nessie Client Initialization ---
# Initialize the Nessie client. In a highly concurrent environment,
# consider if the client needs to be re-initialized per task or managed
# via a connection pool if it's not thread-safe. For now, it's global.
try:
    nessie = NessieClient(api_key=NESSIE_API_KEY)
    logger.info("NessieClient initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize NessieClient: {e}. Please check NESSIE_API_KEY.", exc_info=True)
    # Depending on the application's criticality, you might want to exit here
    # if Nessie is absolutely essential for the application to function.

# --- Database Service Placeholder ---
# This class acts as a placeholder for your actual database interactions.
# In a real application, this would use an ORM (like SQLAlchemy) or a direct
# database client to perform operations.
class DatabaseService:
    def update_user_budget(self, customer_id: str, amount: float, transaction_data: Dict[str, Any]) -> None:
        """Simulates updating a user's budget in the database."""
        logger.info(f"DB: Updating budget for customer {customer_id} with transaction amount {amount}")
        # Example: Replace with actual database write logic
        # self.db_session.query(User).filter_by(id=customer_id).update({'budget': User.budget - amount})
        # self.db_session.commit()
        pass

    def record_transaction(self, customer_id: str, transaction_data: Dict[str, Any]) -> None:
        """Simulates recording a detailed transaction in the database."""
        logger.info(f"DB: Recording transaction for customer {customer_id}")
        # Example: Replace with actual database write logic
        # new_transaction = Transaction(**transaction_data)
        # self.db_session.add(new_transaction)
        # self.db_session.commit()
        pass

    def trigger_notification(self, customer_id: str, message: str) -> None:
        """Simulates sending a notification to the user."""
        logger.info(f"Notification: Triggering for customer {customer_id}: {message}")
        # Example: Integrate with a notification service (e.g., email, push notification)
        pass

    def log_failed_transaction(self, customer_id: str, transaction_data: Dict[str, Any], error_message: str) -> None:
        """Logs a transaction that failed after all retries."""
        logger.error(f"DB: Permanently failed transaction for customer {customer_id}. Data: {transaction_data}. Error: {error_message}")
        # In a real system, this might write to a dead-letter table or trigger an alert.
        pass

# Instantiate the database service
db_service = DatabaseService()

@app.task(bind=True, max_retries=5, default_retry_delay=60) # Added max_retries and default_retry_delay for production robustness
@app.task
def process_transaction(self, transaction_data: Dict[str, Any]) -> None:
    """
    Asynchronously process a transaction fetched from the Nessie API.

    Args:
        transaction_data: A dictionary containing transaction details.
                          Expected keys: 'customer_id', 'amount'.
                          Additional keys like 'description', 'type', etc., are also expected.
    """
    try:
        # --- Data Validation ---
        # Ensure critical data points are present and of the correct type.
        required_keys = ['customer_id', 'amount']
        if not all(key in transaction_data for key in required_keys):
            missing_keys = [key for key in required_keys if key not in transaction_data]
            logger.error(f"Transaction data missing required keys: {missing_keys}. Data: {transaction_data}")
            # Do not retry for invalid input data, as it indicates a programming error or bad input.
            return

        customer_id = str(transaction_data['customer_id']) # Ensure customer_id is treated as a string
        amount = float(transaction_data['amount'])       # Ensure amount is a float for calculations

        logger.info(f"Processing transaction for customer_id: {customer_id}, amount: {amount}. Attempt {self.request.retries + 1}/{self.max_retries + 1}")

        # --- Core Logic: Update budget, record transaction, trigger notifications ---
        db_service.update_user_budget(customer_id, amount, transaction_data)
        db_service.record_transaction(customer_id, transaction_data)
        db_service.trigger_notification(customer_id, f"Your transaction of ${amount:.2f} has been processed.")

        logger.info(f"Successfully processed transaction for customer {customer_id} with amount {amount}.")

    except (ValueError, TypeError) as ve:
        # Catch specific data type/value errors for better error reporting.
        logger.error(f"Data validation error in transaction_data for customer {transaction_data.get('customer_id', 'N/A')}: {ve}. Data: {transaction_data}")
        # No retry for bad input data, as it won't resolve itself.
    except Exception as e:
        # Catch any other unexpected errors during processing.
        logger.error(f"Unexpected error processing transaction for customer {transaction_data.get('customer_id', 'N/A')}: {e}", exc_info=True)

        # --- Advanced Retry Logic with Exponential Backoff ---
        # Celery's `bind=True` allows access to `self` (the task instance).
        # `max_retries` and `default_retry_delay` are set in the decorator.
        # We implement exponential backoff for retries to avoid overwhelming external services.
        if self.request.retries < self.max_retries:
            # Calculate exponential backoff: initial_delay * (2 ^ retries)
            countdown = self.default_retry_delay * (2 ** self.request.retries)
            logger.warning(f"Retrying task process_transaction for customer {customer_id} in {countdown} seconds. Attempt {self.request.retries + 1}/{self.max_retries + 1}")
            raise self.retry(exc=e, countdown=countdown)
        else:
            logger.critical(f"Max retries ({self.max_retries}) reached for transaction processing for customer {customer_id}. Task failed permanently.")
            # After exhausting retries, log the permanent failure and potentially
            # move the transaction to a dead-letter queue or trigger an alert.
            db_service.log_failed_transaction(customer_id, transaction_data, str(e))
