document.addEventListener('DOMContentLoaded', () => {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Handle Config Save
    const saveBtn = document.getElementById('saveConfig');
    const toast = document.getElementById('toast');
    const apiInput = document.getElementById('apiBaseUrl');

    // Load from local storage if previously set
    const savedAPI = localStorage.getItem('ai_suite_api');
    if (savedAPI) {
        apiInput.value = savedAPI;
    }

    saveBtn.addEventListener('click', () => {
        localStorage.setItem('ai_suite_api', apiInput.value);
        toast.classList.remove('hidden');
        
        // Simulating ping to APIs to change status dots
        document.querySelectorAll('.app-card').forEach(card => {
            const status = card.querySelector('.status-indicator');
            status.innerHTML = `<span class="dot online"></span> Ping Successful`;
        });

        setTimeout(() => {
            toast.classList.add('hidden');
        }, 2000);
    });

    // Add 3D tilt effect to cards
    const cards = document.querySelectorAll('.app-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const xPct = x / rect.width - 0.5;
            const yPct = y / rect.height - 0.5;
            
            card.style.transform = `perspective(1000px) rotateX(${yPct * -10}deg) rotateY(${xPct * 10}deg) translateY(-10px)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = `perspective(1000px) rotateX(0) rotateY(0) translateY(0)`;
        });
    });
});
