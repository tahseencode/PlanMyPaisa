# PlanMyPaisa - Asynchronous Financial Transaction Processor

PlanMyPaisa is a web application demonstrating the power of asynchronous task processing for handling financial transactions. It uses a Python-based stack featuring Flask for the web framework and Celery for managing background tasks, providing a non-blocking user experience.

This project was created to showcase a robust backend architecture where long-running processes, like transaction processing, categorization, or notifying users, can be offloaded to background workers, ensuring the web application remains fast and responsive.

## Features

-   **Web Interface:** A clean, simple UI to submit financial transactions.
-   **Asynchronous Processing:** Submitting a transaction immediately queues a background job using Celery, and the user gets an instant response.
-   **Real-Time Status Updates:** The frontend polls the backend to fetch and display the status of the processing task in real-time.
-   **RESTful API:** A clear API for submitting transactions and querying task statuses.
-   **Health Check:** An endpoint to monitor the application's health.
-   **Scalable Architecture:** The use of Celery workers allows for horizontal scaling to handle a high volume of transactions.

## Tech Stack

-   **Backend:** Python, Flask
-   **Asynchronous Tasks:** Celery
-   **Message Broker:** Redis (or RabbitMQ, configurable in Celery)
-   **Frontend:** HTML5, CSS3, vanilla JavaScript
-   **Deployment:** Gunicorn (recommended for production)

## Project Structure

```
.
├── app.py              # Main Flask application, API endpoints
├── tasks.py            # Celery application and task definitions
├── templates
│   └── index.html      # Frontend HTML
├── static
│   ├── css
│   │   └── style.css   # Stylesheet
│   └── js
│       └── app.js      # Frontend JavaScript for form submission and status polling
├── requirements.txt    # Python dependencies
└── README.md
```

## Setup and Installation

### Prerequisites

-   Python 3.8+
-   `pip` (Python package installer)
-   Redis Server (or another Celery-compatible message broker)

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd PlanMyPaisa
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required Python packages:**
    *(Note: You should create a `requirements.txt` file containing `Flask`, `Celery`, and `redis`)*
    ```bash
    pip install Flask Celery redis
    ```

4.  **Install and run Redis:**
    Follow the official installation instructions for your OS: https://redis.io/docs/getting-started/

    Once installed, run the Redis server in a separate terminal:
    ```bash
    redis-server
    ```

## Running the Application

You need to run three separate processes in three different terminal windows. Make sure your virtual environment is activated in the terminals used for the Celery worker and Flask app.

1.  **Terminal 1: Start the Redis Server** (if not already running)
    ```bash
    redis-server
    ```

2.  **Terminal 2: Start the Celery Worker**
    This worker will listen for and execute tasks from the queue.
    ```bash
    # From the project's root directory
    celery -A tasks.app worker --loglevel=info
    ```

3.  **Terminal 3: Start the Flask Web Application**
    ```bash
    # From the project's root directory
    python app.py
    ```

4.  **Access the application:**
    Open your web browser and navigate to `http://127.0.0.1:5000`. You can now submit transactions and see the status updates.

## API Endpoints

The application exposes the following REST API endpoints:

-   `GET /health`
    -   **Description:** Checks the health of the web application.
    -   **Success Response (200):**
        ```json
        {
          "status": "healthy",
          "environment": "development"
        }
        ```

-   `POST /transactions`
    -   **Description:** Submits a new transaction for asynchronous processing.
    -   **Request Body (JSON):**
        ```json
        {
          "customer_id": "CUST-12345",
          "amount": 4.50,
          "description": "Morning coffee at Starbucks"
        }
        ```
    -   **Success Response (202 Accepted):**
        ```json
        {
          "message": "Transaction processing initiated",
          "task_id": "a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890",
          "status_url": "/tasks/a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890"
        }
        ```

-   `GET /tasks/<task_id>`
    -   **Description:** Retrieves the status of a specific task.
    -   **Success Response (200):**
        ```json
        {
          "state": "SUCCESS",
          "info": { /* task result */ }
        }
        ```

## License

This is a demo project and is not intended for production use without further development. It can be considered under the MIT License.