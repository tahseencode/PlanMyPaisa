# tasks.py
import os
import logging
import time
from celery import Celery
from typing import Dict, Any

# --- Configuration ---
# Load configuration from environment variables for flexibility and security.
# Provide sensible defaults for development, but ensure they are set in production.
REDIS_BROKER_URL = os.getenv('REDIS_BROKER_URL', 'redis://localhost:6379/0')

# --- Logging Setup ---
# Configure a robust logging system instead of simple print statements.
# This allows for better monitoring, debugging, and log management.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Celery App Initialization ---
app = Celery('tasks', broker=REDIS_BROKER_URL)

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

# --- "Smart" Feature: Transaction Categorization ---
# This is a simplified, rule-based categorizer. In a real-world scenario,
# this could be a machine learning model or a more complex rules engine.
def categorize_transaction(description: str) -> str:
    """Categorizes a transaction based on its description."""
    description = description.lower()
    if any(keyword in description for keyword in ['coffee', 'starbucks', 'cafe']):
        return 'Food & Drink'
    if any(keyword in description for keyword in ['uber', 'lyft', 'taxi']):
        return 'Transport'
    if any(keyword in description for keyword in ['amazon', 'shopping', 'store']):
        return 'Shopping'
    if any(keyword in description for keyword in ['rent', 'mortgage']):
        return 'Housing'
    if any(keyword in description for keyword in ['netflix', 'spotify', 'hulu']):
        return 'Entertainment'
    return 'Miscellaneous'

# Instantiate the database service
db_service = DatabaseService()

@app.task(bind=True, max_retries=10, default_retry_delay=60)
def process_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Asynchronously process a transaction, categorize it, and report progress.

    Args:
        transaction_data: A dictionary containing transaction details.
                          Expected keys: 'customer_id', 'amount', 'description'.
    
    Returns:
        A dictionary with the result of the processing.
    """
    try:
        # --- Progress Reporting: Initial State ---
        self.update_state(state='PROGRESS', meta={'status': 'Initiated...'})
        time.sleep(1) # Simulate initial work

        # --- Data Validation ---
        self.update_state(state='PROGRESS', meta={'status': 'Validating transaction data...'})
        time.sleep(1)
        required_keys = ['customer_id', 'amount', 'description'] # Added 'description'
        if not all(key in transaction_data for key in required_keys):
            missing_keys = [key for key in required_keys if key not in transaction_data]
            logger.error(f"Transaction data missing required keys: {missing_keys}. Data: {transaction_data}")
            # Do not retry for invalid input data. Mark as failed.
            self.update_state(state='FAILURE', meta={'status': f"Invalid input: Missing {', '.join(missing_keys)}"})
            return {'status': 'Failed', 'reason': f"Missing required keys: {', '.join(missing_keys)}"}

        customer_id = str(transaction_data['customer_id'])
        amount = float(transaction_data['amount'])
        description = str(transaction_data['description'])

        logger.info(f"Processing transaction for customer_id: {customer_id}, amount: {amount}. Attempt {self.request.retries + 1}/{self.max_retries + 1}")

        # --- "Smart" Feature: Categorization ---
        self.update_state(state='PROGRESS', meta={'status': f"Categorizing: '{description}'..."})
        time.sleep(1.5) # Simulate ML model thinking :)
        category = categorize_transaction(description)
        transaction_data['category'] = category
        logger.info(f"Transaction for customer {customer_id} categorized as '{category}'.")
        self.update_state(state='PROGRESS', meta={'status': f"Categorized as '{category}'. Updating records..."})
        time.sleep(1)

        # --- Core Logic: Update budget, record transaction, trigger notifications ---
        db_service.update_user_budget(customer_id, amount, transaction_data)
        db_service.record_transaction(customer_id, transaction_data)
        db_service.trigger_notification(customer_id, f"Your transaction of ${amount:.2f} ('{description}') has been processed.")

        logger.info(f"Successfully processed transaction for customer {customer_id} with amount {amount}.")

        # --- Progress Reporting: Final State ---
        # The 'info' dict in the final result is what the client sees.
        return {'status': 'Complete', 'customer_id': customer_id, 'amount': amount, 'category': category}

    except (ValueError, TypeError) as ve:
        logger.error(f"Data validation error for customer {transaction_data.get('customer_id', 'N/A')}: {ve}. Data: {transaction_data}")
        self.update_state(state='FAILURE', meta={'status': f"Data validation error: {ve}"})
        return {'status': 'Failed', 'reason': str(ve)} # Return failure info
    except Exception as e:
        logger.error(f"Unexpected error processing transaction for customer {transaction_data.get('customer_id', 'N/A')}: {e}", exc_info=True)

        # --- Advanced Retry Logic with Exponential Backoff ---
        try:
            countdown = self.default_retry_delay * (2 ** self.request.retries)
            logger.warning(f"Retrying task for customer {customer_id} in {countdown} seconds. Attempt {self.request.retries + 1}/{self.max_retries + 1}")
            # Update state to show it's retrying
            self.update_state(state='RETRY', meta={'status': f"Service unavailable. Retrying in {countdown}s..."})
            raise self.retry(exc=e, countdown=countdown)
        except self.MaxRetriesExceededError:
            logger.critical(f"Max retries reached for customer {customer_id}. Task failed permanently.")
            db_service.log_failed_transaction(customer_id, transaction_data, str(e))
            # Update state to permanent failure
            self.update_state(state='FAILURE', meta={'status': 'Permanent failure after multiple retries.'})
            return {'status': 'Failed Permanently', 'reason': str(e)}
