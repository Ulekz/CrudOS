function rollDice() {
    return Math.floor(Math.random() * 6) + 1;
}

function updateDice() {
    const dice1 = document.getElementById('dice1');
    const dice2 = document.getElementById('dice2');
    
    const roll1 = rollDice();
    const roll2 = rollDice();
    
    const faces1 = dice1.children;
    const faces2 = dice2.children;
    
    for (let i = 0; i < faces1.length; i++) {
        faces1[i].style.display = 'none';
        faces2[i].style.display = 'none';
    }
    
    faces1[roll1 - 1].style.display = 'flex';
    faces2[roll2 - 1].style.display = 'flex';
    
    dice1.style.transform = `rotateX(${getRotationX(roll1)}deg) rotateY(${getRotationY(roll1)}deg)`;
    dice2.style.transform = `rotateX(${getRotationX(roll2)}deg) rotateY(${getRotationY(roll2)}deg)`;
}

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

setInterval(updateDice, 2000); // Cambiar los números de los dados cada 2 segundos
