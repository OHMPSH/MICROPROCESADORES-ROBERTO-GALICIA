const keys = document.querySelectorAll('.key');
const statusText = document.getElementById('status');
const picoIp = '192.168.100.14'; // ⚠️ Reemplaza esta IP con la de tu Pico W

keys.forEach(key => {
    key.addEventListener('click', () => {
        const keyValue = key.getAttribute('data-key');
        console.log(`Tecla presionada: ${keyValue}`);
        statusText.textContent = `Tecla ${keyValue} seleccionada.`;
        sendStatus(keyValue);
    });
});

/**
 * Envía el valor seleccionado al microcontrolador usando Fetch API.
 * @param {string} value - El valor (1-9) a enviar.
 */
async function sendStatus(value) {
    statusText.textContent = 'Enviando comando...';
    const url = `http://${picoIp}/control?key=${value}`;
    
    try {
        const response = await fetch(url);
        
        if (response.ok) {
            const data = await response.json();
            statusText.textContent = `Respuesta del Pico: ${data.message}`;
        } else {
            statusText.textContent = `Error al conectar: ${response.statusText}`;
            console.error('Error en la respuesta del servidor:', response.status);
        }
    } catch (error) {
        statusText.textContent = `Error de red: ${error.message}`;
        console.error('Error de red:', error);
    }
}