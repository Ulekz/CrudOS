document.addEventListener('DOMContentLoaded', () => {
    const modeToggle = document.getElementById('mode-toggle');
    const body = document.body;
    const navbar = document.querySelector('.navbar');
    const formContainers = document.querySelectorAll('.form-container form input, .form-container');

    modeToggle.addEventListener('click', () => {
        const isDarkMode = body.classList.toggle('dark-mode');
        body.classList.toggle('light-mode', !isDarkMode);
        navbar.classList.toggle('dark-mode', isDarkMode);
        navbar.classList.toggle('light-mode', !isDarkMode);
        formContainers.forEach(container => {
            container.classList.toggle('dark-mode', isDarkMode);
            container.classList.toggle('light-mode', !isDarkMode);
        });
        modeToggle.textContent = isDarkMode ? 'Modo Claro' : 'Modo Oscuro';
        localStorage.setItem('mode', isDarkMode ? 'dark' : 'light');
    });

    if (localStorage.getItem('mode') === 'dark') {
        body.classList.add('dark-mode');
        body.classList.remove('light-mode');
        navbar.classList.add('dark-mode');
        navbar.classList.remove('light-mode');
        formContainers.forEach(container => {
            container.classList.add('dark-mode');
            container.classList.remove('light-mode');
        });
        modeToggle.textContent = 'Modo Claro';
    } else {
        body.classList.add('light-mode');
        body.classList.remove('dark-mode');
        navbar.classList.add('light-mode');
        navbar.classList.remove('dark-mode');
        formContainers.forEach(container => {
            container.classList.add('light-mode');
            container.classList.remove('dark-mode');
        });
        modeToggle.textContent = 'Modo Oscuro';
    }
});
