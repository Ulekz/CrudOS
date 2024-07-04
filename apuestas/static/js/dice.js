// Función para generar un número aleatorio entre 1 y 6
function rollDice() {
    return Math.floor(Math.random() * 6) + 1;
}

// Función para actualizar los dados en la página
function updateDice() {
    const dice1 = document.getElementById('dice1');
    const dice2 = document.getElementById('dice2');
    
    const roll1 = rollDice(); // Obtener número aleatorio para el primer dado
    const roll2 = rollDice(); // Obtener número aleatorio para el segundo dado
    
    const faces1 = dice1.children; // Obtener las caras del primer dado
    const faces2 = dice2.children; // Obtener las caras del segundo dado
    
    // Ocultar todas las caras de ambos dados
    for (let i = 0; i < faces1.length; i++) {
        faces1[i].style.display = 'none';
        faces2[i].style.display = 'none';
    }
    
    // Mostrar la cara correspondiente al número aleatorio generado
    faces1[roll1 - 1].style.display = 'flex';
    faces2[roll2 - 1].style.display = 'flex';
    
    // Aplicar la rotación 3D correspondiente a cada dado
    dice1.style.transform = `rotateX(${getRotationX(roll1)}deg) rotateY(${getRotationY(roll1)}deg)`;
    dice2.style.transform = `rotateX(${getRotationX(roll2)}deg) rotateY(${getRotationY(roll2)}deg)`;
}

// Función para obtener el ángulo de rotación en el eje X según la cara del dado
function getRotationX(face) {
    switch(face) {
        case 1: return 0;
        case 2: return 0;
        case 3: return 0;
        case 4: return 0;
        case 5: return 90;
        case 6: return -90;
        default: return 0;
    }
}

// Función para obtener el ángulo de rotación en el eje Y según la cara del dado
function getRotationY(face) {
    switch(face) {
        case 1: return 0;
        case 2: return 180;
        case 3: return 90;
        case 4: return -90;
        case 5: return 0;
        case 6: return 0;
        default: return 0;
    }
}

// Actualizar los dados cada 2 segundos
setInterval(updateDice, 2000);
