// c:\PlanMyPaisa\static\js\app.js

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('transaction-form');
    const statusEl = document.getElementById('task-status-content');
    const submitBtn = document.getElementById('submit-btn');

    let pollingInterval;

    // Function to poll for task status
    const pollTaskStatus = async (statusUrl) => {
        try {
            const response = await fetch(statusUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            // Update the status display
            statusEl.textContent = JSON.stringify(data, null, 2);

            // Stop polling if the task is finished (SUCCESS, FAILURE)
            if (data.state === 'SUCCESS' || data.state === 'FAILURE') {
                clearInterval(pollingInterval);
                submitBtn.disabled = false;
                submitBtn.textContent = 'Process Transaction';

                // Add a visual cue for success/failure
                if (data.state === 'SUCCESS') {
                    statusEl.style.backgroundColor = '#00A896'; // var(--color-primary)
                } else {
                    statusEl.style.backgroundColor = '#D90429'; // var(--color-alert)
                }
            }

        } catch (error) {
            console.error('Polling error:', error);
            statusEl.textContent = JSON.stringify({ error: 'Failed to get task status.' }, null, 2);
            clearInterval(pollingInterval);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Process Transaction';
        }
    };

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Clear previous polling and reset UI
        if (pollingInterval) {
            clearInterval(pollingInterval);
        }
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
        statusEl.style.backgroundColor = 'var(--color-text-dark)'; // Reset color
        statusEl.textContent = JSON.stringify({ status: 'Initiating request...' }, null, 2);

        const formData = new FormData(form);
        const data = {
            customer_id: formData.get('customer_id'),
            amount: parseFloat(formData.get('amount')),
            description: formData.get('description'),
        };

        try {
            const response = await fetch('/transactions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();
            statusEl.textContent = JSON.stringify(result, null, 2);

            if (response.status === 202 && result.status_url) {
                // Start polling the status URL
                pollingInterval = setInterval(() => pollTaskStatus(result.status_url), 1000);
            } else {
                // Handle immediate errors from the Flask endpoint
                throw new Error(result.error || 'Failed to initiate task.');
            }

        } catch (error) {
            console.error('Submission error:', error);
            statusEl.textContent = JSON.stringify({ error: error.message }, null, 2);
            statusEl.style.backgroundColor = '#D90429'; // var(--color-alert)
            submitBtn.disabled = false;
            submitBtn.textContent = 'Process Transaction';
        }
    });
});