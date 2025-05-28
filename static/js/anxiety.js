document.addEventListener('DOMContentLoaded', function () {
    const range = document.getElementById('anxietyRange');
    const message = document.getElementById('anxietyMessage');
    const helpBtn = document.getElementById('helpBtn');
    
    let animationFrameId = null;

    function updateAnxietyMessage(level) {
        let text = "Estado: ";
        let className = "neutral";

        if (level <= 2) {
            text += "Muy relajado 😊. ¡Disfruta tu vuelo!";
            className = "relaxed";
        } else if (level <= 4) {
            text += "Relajado 🙂. Todo está bajo control.";
            className = "relaxed";
        } else if (level <= 6) {
            text += "Neutral 😐. Mantén la calma.";
            className = "neutral";
        } else if (level <= 8) {
            text += "Ansioso 😟. Prueba una técnica de relajación.";
            className = "anxious";
        } else {
            text += "Muy ansioso 😰. Una azafata te asistirá pronto.";
            className = "anxious";
        }

        // Cambiar texto y clase con transición suave
        if (message.textContent !== text) {
            message.style.opacity = 0; // inicia fade-out
            setTimeout(() => {
                message.textContent = text;
                message.className = `anxiety-status ${className}`;
                message.style.opacity = 1; // fade-in
            }, 200);
        } else {
            // si mismo texto, solo actualizamos clase para el color
            message.className = `anxiety-status ${className}`;
        }

        // Animación de pulso para ansiedad alta (>7)
        if (level > 7) {
            message.style.animation = "pulse 1.5s infinite ease-in-out";
        } else {
            message.style.animation = "none";
        }
    }

    function onRangeInput() {
        const level = parseFloat(range.value); // Más exacto, permite decimales
        // Cancelar animación previa para evitar lags
        if (animationFrameId) cancelAnimationFrame(animationFrameId);
        animationFrameId = requestAnimationFrame(() => updateAnxietyMessage(level));
    }

    range.addEventListener('input', onRangeInput);

    // Inicializar estado al cargar la página
    updateAnxietyMessage(parseFloat(range.value));

    // Help button
    helpBtn.addEventListener('click', () => {
        alert("¡Una azafata viene en camino para ayudarte! Respira profundamente mientras esperas.");
    });
    
    // Sound controls
    const playButtons = document.querySelectorAll('.play-btn');
    playButtons.forEach(button => {
        button.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon.classList.contains('fa-play')) {
                icon.classList.remove('fa-play');
                icon.classList.add('fa-pause');
                this.style.background = "var(--warning)";
            } else {
                icon.classList.remove('fa-pause');
                icon.classList.add('fa-play');
                this.style.background = "var(--primary)";
            }
        });
    });
    
    // Breathing exercise
    let breathPhase = document.getElementById("breathPhase");
    let breathProgressCircle = document.getElementById("breathProgressCircle");
    let breathCountElement = document.getElementById("breathCount");
    let breathIntervals = [4, 7, 8]; // Inhale, hold, exhale times
    let phaseIndex = 0;
    let cycle = 0;
    let timer = null;
    let currentSec = 0;
    let isPaused = false;
    
    function updateBreathingDisplay() {
        const labels = ["Inhala", "Mantén", "Exhala"];
        const colors = ["#4ade80", "#fbbf24", "#f87171"];
        breathPhase.textContent = labels[phaseIndex];
        breathProgressCircle.style.background = `conic-gradient(${colors[phaseIndex]} ${(currentSec / breathIntervals[phaseIndex]) * 100}%, transparent 0%)`;
        breathCountElement.textContent = cycle;
    }
    
    window.startBreathing = function () {
        if (timer && !isPaused) return;
        
        if (isPaused) {
            isPaused = false;
        } else {
            phaseIndex = 0;
            currentSec = 0;
            cycle = 0;
        }
        
        breathPhase.parentElement.parentElement.classList.add("breathing");
        updateBreathingDisplay();
        
        clearInterval(timer);
        timer = setInterval(() => {
            if (isPaused) return;
            
            currentSec++;
            updateBreathingDisplay();
            
            if (currentSec >= breathIntervals[phaseIndex]) {
                currentSec = 0;
                phaseIndex = (phaseIndex + 1) % 3;
                if (phaseIndex === 0) cycle++;
                updateBreathingDisplay();
            }
        }, 1000);
    };
    
    window.pauseBreathing = function () {
        isPaused = true;
        breathPhase.parentElement.parentElement.classList.remove("breathing");
    };
    
    window.stopBreathing = function () {
        clearInterval(timer);
        timer = null;
        isPaused = false;
        phaseIndex = 0;
        currentSec = 0;
        cycle = 0;
        breathPhase.parentElement.parentElement.classList.remove("breathing");
        breathProgressCircle.style.background = "conic-gradient(var(--accent) 0%, transparent 0%)";
        breathPhase.textContent = "Inhala";
        breathCountElement.textContent = "0";
    };
    
    // Animate fact cards on load
    const factCards = document.querySelectorAll('.fact-card');
    factCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.2}s`;
    });
});
