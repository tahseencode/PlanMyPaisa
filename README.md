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
   **Frontend:** React, React Three Fiber (for 3D), Framer Motion (for animation)
-   **Deployment:** Gunicorn (recommended for production)

## Project Structure

```
.
├── app.py              # Main Flask application, API endpoints
├── tasks.py            # Celery application and task definitions
├── app.js              # Root React component
├── templates
│   └── index.html      # Frontend HTML
├── static
│   ├── css
│   │   └── style.css   # Stylesheet
├── package.json        # Frontend dependencies (assumed for React)
├── requirements.txt    # Python dependencies
└── README.md
```

## Setup and Installation

### Prerequisites

-   Python 3.8+
-   `pip` (Python package installer)
-   Redis Server (or another Celery-compatible message broker)
-   Node.js and npm (for the React frontend)

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

    # Note for Windows users: If you get an error about script execution being disabled,
    # run the following command in your PowerShell terminal (you may need to run as Administrator),
    # then try activating again:
    # Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    # Alternatively, you can use Command Prompt (cmd.exe) and run: venv\Scripts\activate.bat
    ```

3.  **Install the required Python packages:**
    (Make sure your virtual environment is activated)
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install frontend dependencies:**
    ```bash
    npm install
    ```

5.  **Install and run Redis:**
    While Redis doesn't officially support Windows, a community-maintained version is available and works well for development.

    **On Windows (Native):**
    1.  Go to the latest releases of the unofficial Windows port on GitHub: https://github.com/tporadowski/redis/releases.
    2.  Download the latest `.msi` installer (e.g., `Redis-x.x.x-x64-xxx.msi`).
    3.  Run the installer. **Important:** During setup, make sure to check the box that says **"Add the Redis installation folder to the PATH environment variable."**
    4.  Once installed, you can open a new Command Prompt or PowerShell window and start the Redis server with the command below.

    **On macOS/Linux:**
    Follow the official installation instructions for your OS: https://redis.io/docs/getting-started/

## Running the Application

This project has a separate backend (Flask/Celery) and frontend (React). You will need to run them concurrently in separate terminals.

### Backend

1.  **Terminal 1: Start Redis**
    If it's not already running from the installation step, open a new terminal and start the Redis server. It will run in this window.
    ```bash
    redis-server
    ```

2.  **Terminal 2: Start the Celery Worker**
    This worker will listen for and execute background tasks. Make sure your Python virtual environment is activated.
    ```bash
    # From the project's root directory
    celery -A tasks.app worker --loglevel=info
    ```

3.  **Terminal 3: Start the Flask API Server**
    This runs the backend API that the frontend will communicate with. Make sure your Python virtual environment is activated.
    ```bash
    # From the project's root directory
    python app.py
    ```
    The API will be running at `http://127.0.0.1:5000`.

### Frontend

4.  **Terminal 4: Start the React Development Server**
    This will serve the user interface.
    ```bash
    npm start
    ```
    *Note for Windows users:* If you get a `PSSecurityException` error, your PowerShell terminal is blocking the script. Run the following command first, then try `npm start` again:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    ```
    This command will typically open a new browser tab. If not, navigate to `http://localhost:3000` (or whatever port is indicated in the terminal). The React application is configured to send API requests to your Flask backend.

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