/* c:\PlanMyPaisa\static\js\main.js */
document.addEventListener('DOMContentLoaded', () => {
    // Stagger animation for ghost events
    const ghostEvents = document.querySelectorAll('.ghost-event');
    ghostEvents.forEach((event, index) => {
        event.style.setProperty('--delay', `${0.5 + index * 0.3}s`);
    });

    // --- Interactive Demo Logic ---
    const transactionForm = document.getElementById('transaction-form');
    const statusContent = document.getElementById('task-status-content');
    const originalStatusBgColor = statusContent ? getComputedStyle(statusContent).backgroundColor : '';

    if (transactionForm && statusContent) {
        transactionForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(transactionForm);
            const data = {
                customer_id: formData.get('customer_id'),
                amount: parseFloat(formData.get('amount')),
            };

            // Reset status UI
            statusContent.style.backgroundColor = originalStatusBgColor;
            statusContent.innerHTML = `<p>Submitting transaction...</p>`;

            try {
                const response = await fetch('/transactions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.error || `HTTP error! Status: ${response.status}`);
                }

                statusContent.innerHTML = `<p>✅ Task dispatched! ID: ${result.task_id}</p><p>Polling for status...</p>`;
                pollTaskStatus(result.status_url);

            } catch (error) {
                statusContent.innerHTML = `<p style="color: var(--color-alert);">❌ Error: ${error.message}</p>`;
                console.error('Submission error:', error);
            }
        });
    }

    function pollTaskStatus(statusUrl) {
        const interval = setInterval(async () => {
            try {
                const response = await fetch(statusUrl);
                const result = await response.json();

                const formattedStatus = JSON.stringify(result, null, 2);
                statusContent.innerHTML = `<pre>${formattedStatus}</pre>`;

                if (result.state === 'SUCCESS' || result.state === 'FAILURE') {
                    clearInterval(interval);
                    statusContent.style.backgroundColor = result.state === 'SUCCESS' ? 'var(--color-primary)' : 'var(--color-alert)';
                }
            } catch (error) {
                clearInterval(interval);
                statusContent.innerHTML = `<p style="color: var(--color-alert);">❌ Error polling status: ${error.message}</p>`;
            }
        }, 2000); // Poll every 2 seconds
    }
});