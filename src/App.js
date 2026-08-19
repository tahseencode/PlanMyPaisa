import React from 'react';
import { motion } from 'framer-motion';
import InteractiveDemo from './components/InteractiveDemo';
import HeroAnimation from './components/HeroAnimation';

const App = () => {
    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.2,
            },
        },
    };

    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: {
            y: 0,
            opacity: 1,
            transition: {
                duration: 0.6,
                ease: 'easeOut',
            },
        },
    };

    return (
        <div className="app-container">
            <header className="site-header">
                <div className="logo">PlanMyPaisa</div>
            </header>

            <main>
                <motion.section
                    className="hero-section"
                    initial="hidden"
                    animate="visible"
                    variants={containerVariants}
                >
                    <HeroAnimation />
                    <motion.h1 variants={itemVariants}>Process Finances, Instantly.</motion.h1>
                    <motion.p className="hero-subtitle" variants={itemVariants}>
                        A demonstration of a non-blocking, asynchronous backend architecture using Python, Celery, and React.
                    </motion.p>
                </motion.section>
                <InteractiveDemo />
            </main>
        </div>
    );
};

export default App;