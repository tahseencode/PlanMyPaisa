import React, { useEffect } from 'react';
import InteractiveDemo from './components/InteractiveDemo';

// --- Placeholder Components ---
// In a real application, these would be in their own files inside './components/'

const Header = () => (
    <header className="site-header">
        <div className="container">
            <a href="/" className="logo">PlanMyPaisa</a>
            <nav className="main-nav">
                <ul>
                    <li><a href="#features">Features</a></li>
                    <li><a href="#demo">Demo</a></li>
                    <li><a href="#signup">Sign Up</a></li>
                </ul>
            </nav>
        </div>
    </header>
);

const Hero = () => {
    // This effect replicates the stagger animation from main.js
    useEffect(() => {
        const ghostEvents = document.querySelectorAll('.ghost-event');
        ghostEvents.forEach((event, index) => {
            event.style.setProperty('--delay', `${0.5 + index * 0.3}s`);
        });
    }, []); // Run only once on mount

    // Dummy data for calendar days
    const days = Array.from({ length: 35 }, (_, i) => i - 1);
    const eventDays = [4, 6, 10, 17, 24];

    return (
        <section className="hero-section">
            <div className="hero-calendar-container">
                <div className="planmypaisa-calendar">
                    <div className="calendar-header">October 2026</div>
                    <div className="calendar-grid">
                        {days.map((day, index) => (
                            <div
                                key={index}
                                className={`day ${eventDays.includes(index) ? 'has-event ghost-event' : ''}`}
                                data-event={eventDays.includes(index) ? 'Auto-Pay: Bill' : ''}
                            >
                                {day > 0 && day < 32 ? day : ''}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
            <div className="hero-content">
                <h1>Intelligent Financial Planning, Simplified.</h1>
                <p className="body-large">PlanMyPaisa uses asynchronous tasks to categorize your spending without blocking your experience. See it in action below.</p>
            </div>
        </section>
    );
};

const Features = () => (
    <section id="features" className="features-section">
        <div className="container">
            <div className="section-heading">
                <h2>Why PlanMyPaisa?</h2>
                <p className="body-large">Our backend is built for reliability and scale.</p>
            </div>
            <div className="feature-item">
                <div className="feature-text">
                    <h3 className="feature-title">Asynchronous Processing</h3>
                    <p>Never wait for a page to load. We process your transactions in the background, ensuring a snappy user experience every time.</p>
                </div>
                <div className="feature-visual" />
            </div>
            <div className="feature-item reverse">
                <div className="feature-text">
                    <h3 className="feature-title">Smart Categorization</h3>
                    <p>Our "smart" engine analyzes transaction descriptions to automatically categorize your spending, giving you clear insights into your financial habits.</p>
                </div>
                <div className="feature-visual" />
            </div>
        </div>
    </section>
);

const CTA = () => (
    <section id="signup" className="cta-section">
        <div className="container">
            <h2 className="section-heading">Ready to Take Control?</h2>
            <p className="body-large">Start your journey towards financial clarity today.</p>
            <a href="#signup" className="btn btn-large">Get Started for Free</a>
        </div>
    </section>
);

const Footer = () => (
    <footer className="site-footer">
        <div className="container">
            <p>&copy; 2026 PlanMyPaisa. All rights reserved.</p>
        </div>
    </footer>
);

function App() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <Features />
        <section id="demo" className="container" style={{ paddingTop: 'var(--spacing-xl)', paddingBottom: 'var(--spacing-xl)' }}>
            <InteractiveDemo />
        </section>
        <CTA />
      </main>
      <Footer />
    </>
  );
}

export default App;