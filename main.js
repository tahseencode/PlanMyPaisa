/* c:\PlanMyPaisa\static\js\main.js */
document.addEventListener('DOMContentLoaded', () => {
    const ghostEvents = document.querySelectorAll('.ghost-event');
    ghostEvents.forEach((event, index) => {
        // Stagger animation delay to make the ghost events appear sequentially
        event.style.setProperty('--delay', `${0.5 + index * 0.3}s`);
    });
});