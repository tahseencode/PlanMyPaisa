import React, { useState, useEffect, useRef } from 'react';

const InteractiveDemo = () => {
    // Form state
    const [customerId, setCustomerId] = useState('CUST-12345');
    const [amount, setAmount] = useState('29.99');
    const [description, setDescription] = useState('Monthly Subscription');

    // Task state
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [statusUrl, setStatusUrl] = useState(null);
    const [taskStatus, setTaskStatus] = useState({ status: 'Ready to process a transaction.' });
    const [polling, setPolling] = useState(false);

    const pollingIntervalRef = useRef(null);

    // Effect for polling
    useEffect(() => {
        if (!statusUrl || !polling) {
            if (pollingIntervalRef.current) clearInterval(pollingIntervalRef.current);
            return;
        }

        pollingIntervalRef.current = setInterval(async () => {
            try {
                const response = await fetch(statusUrl);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                
                const data = await response.json();
                setTaskStatus(data);

                if (['SUCCESS', 'FAILURE', 'Failed Permanently'].includes(data.state)) {
                    setPolling(false);
                    setIsSubmitting(false);
                }
            } catch (error) {
                console.error('Polling error:', error);
                setTaskStatus({ state: 'FAILURE', info: { error: 'Failed to get task status.' } });
                setPolling(false);
                setIsSubmitting(false);
            }
        }, 2000); // Poll every 2 seconds

        return () => clearInterval(pollingIntervalRef.current);
    }, [statusUrl, polling]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (pollingIntervalRef.current) clearInterval(pollingIntervalRef.current);
        setIsSubmitting(true);
        setPolling(false);
        setStatusUrl(null);
        setTaskStatus({ status: 'Initiating request...' });

        const transactionData = {
            customer_id: customerId,
            amount: parseFloat(amount),
            description: description,
        };

        try {
            const response = await fetch('/transactions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(transactionData),
            });

            const result = await response.json();
            setTaskStatus(result);

            if (response.status === 202 && result.status_url) {
                setStatusUrl(result.status_url);
                setPolling(true);
            } else {
                throw new Error(result.error || 'Failed to initiate task.');
            }
        } catch (error) {
            console.error('Submission error:', error);
            setTaskStatus({ state: 'FAILURE', info: { error: error.message } });
            setIsSubmitting(false);
        }
    };

    const getStatusBgColor = () => {
        if (!taskStatus?.state) return 'var(--color-text-dark)';
        switch (taskStatus.state) {
            case 'SUCCESS': return 'var(--color-primary)';
            case 'FAILURE': return 'var(--color-alert)';
            case 'RETRY': return 'var(--color-accent)';
            default: return 'var(--color-text-dark)';
        }
    };

    return (
        <div className="demo-grid">
            <div className="form-container">
                <h3 className="feature-title">Interactive Demo</h3>
                <p>Submit a sample transaction to see the asynchronous background processing in action. The status on the right will update in real-time.</p>
                <form id="transaction-form" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="customer_id">Customer ID</label>
                        <input type="text" id="customer_id" name="customer_id" value={customerId} onChange={e => setCustomerId(e.target.value)} required />
                    </div>
                    <div className="form-group">
                        <label htmlFor="amount">Amount ($)</label>
                        <input type="number" id="amount" name="amount" step="0.01" value={amount} onChange={e => setAmount(e.target.value)} required />
                    </div>
                    <div className="form-group">
                        <label htmlFor="description">Description</label>
                        <input type="text" id="description" name="description" value={description} onChange={e => setDescription(e.target.value)} required />
                    </div>
                    <button type="submit" id="submit-btn" className="btn btn-primary" disabled={isSubmitting}>
                        {isSubmitting ? 'Processing...' : 'Process Transaction'}
                    </button>
                </form>
            </div>
            <div className="status-container">
                <h3 className="feature-title">Task Status</h3>
                <p>The raw JSON response from the status endpoint will appear here.</p>
                <div id="task-status-content" style={{ backgroundColor: getStatusBgColor() }}>
                    <pre>{JSON.stringify(taskStatus, null, 2)}</pre>
                </div>
            </div>
        </div>
    );
};

export default InteractiveDemo;