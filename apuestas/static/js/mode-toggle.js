// Esperar a que el DOM esté completamente cargado antes de ejecutar el script
document.addEventListener('DOMContentLoaded', () => {
    // Seleccionar el botón para alternar el modo
    const modeToggle = document.getElementById('mode-toggle');
    // Seleccionar el cuerpo del documento
    const body = document.body;
    // Seleccionar la barra de navegación
    const navbar = document.querySelector('.navbar');
    // Seleccionar todos los contenedores de formularios y los inputs dentro de ellos
    const formContainers = document.querySelectorAll('.form-container, .form-container form input');

    // Función para establecer el modo claro u oscuro
    const setMode = (isDarkMode) => {
        // Alternar clases para el cuerpo del documento
        body.classList.toggle('dark-mode', isDarkMode);
        body.classList.toggle('light-mode', !isDarkMode);
        // Alternar clases para la barra de navegación
        navbar.classList.toggle('dark-mode', isDarkMode);
        navbar.classList.toggle('light-mode', !isDarkMode);
        // Alternar clases para los contenedores de formularios e inputs
        formContainers.forEach(container => {
            container.classList.toggle('dark-mode', isDarkMode);
            container.classList.toggle('light-mode', !isDarkMode);
        });
        // Actualizar el texto del botón para alternar el modo
        modeToggle.textContent = isDarkMode ? 'Modo Claro' : 'Modo Oscuro';
    };

    // Event listener para alternar el modo cuando se haga clic en el botón
    modeToggle.addEventListener('click', () => {
        const isDarkMode = !body.classList.contains('dark-mode');
        setMode(isDarkMode);
        // Guardar la preferencia del modo en localStorage
        localStorage.setItem('mode', isDarkMode ? 'dark' : 'light');
    });

    // Establecer el modo basado en la preferencia guardada en localStorage
    const savedMode = localStorage.getItem('mode') === 'dark';
    setMode(savedMode);
});
