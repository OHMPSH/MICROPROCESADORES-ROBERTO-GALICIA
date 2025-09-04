# main.py en el Raspberry Pi Pico W
# Importa las librerías necesarias para el funcionamiento del código
import network    # Permite la conexión a redes WiFi
import socket     # Para crear un servidor web y manejar conexiones de red
import time       # Para controlar el tiempo, como los retrasos entre pasos
from machine import Pin   # Para controlar los pines del microcontrolador
import json       # Para trabajar con datos en formato JSON (como la respuesta al navegador)

# Define el pin del LED integrado de la placa como salida
led_onboard = Pin("LED", Pin.OUT)

# Configuración de tu red WiFi
ssid = ''
password = ''

# Configuración de los pines de los LEDs que se van a usar, en una lista
led_pins = [Pin(16, Pin.OUT), Pin(17, Pin.OUT), Pin(18, Pin.OUT), Pin(19, Pin.OUT),
            Pin(20, Pin.OUT), Pin(21, Pin.OUT), Pin(22, Pin.OUT), Pin(26, Pin.OUT)]

# Variables globales que definen el estado actual de la "máquina de estados"
current_sequence_name = None  # Guarda el nombre de la secuencia de LEDs que se está ejecutando
sequence_step = 0            # Almacena el paso actual de la secuencia
last_step_time = 0           # Guarda el tiempo en milisegundos del último cambio de estado
step_delay = 100             # Retraso en milisegundos entre cada paso de la secuencia

# Conectar a la red WiFi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF) # Crea una instancia de la interfaz WiFi
    wlan.active(True)                     # Activa el modo estación (cliente)
    print("Conectando a la red:", ssid)
    led_onboard.value(1)                  # Enciende el LED de la placa para indicar que está conectándose
    wlan.connect(ssid, password)          # Inicia la conexión a la red
    
    max_attempts = 15                     # Número máximo de intentos para conectarse
    attempts = 0                          # Contador de intentos
    while not wlan.isconnected() and attempts < max_attempts: # Bucle de espera mientras no esté conectado
        print('.', end='')                # Imprime un punto para mostrar que está intentando
        time.sleep(1)                     # Pausa de 1 segundo
        attempts += 1                     # Incrementa el contador de intentos

    if wlan.isconnected():                # Si la conexión fue exitosa
        print('\nConexión exitosa. Dirección IP:', wlan.ifconfig()[0]) # Muestra la IP asignada
        return wlan                       # Devuelve el objeto WLAN
    else:                                 # Si la conexión falló
        print('\nFallo la conexión a la red. Revisa el SSID y la contraseña.')
        led_onboard.value(0)              # Apaga el LED para indicar el fallo
        return None

# Función para apagar todos los LEDs en la lista `led_pins`
def turn_off_all_leds():
    for pin in led_pins:                  # Recorre la lista de pines de los LEDs
        pin.value(0)                      # Establece el valor del pin en 0 (apagado)
    print("Todos los LEDs están apagados.")
    
# --- Funciones de Secuencia de LEDs (un solo paso) ---
# Enciende un LED de izquierda a derecha en cada llamada
def next_step_izq_der():
    global sequence_step                  # Declara que se usará la variable global
    turn_off_all_leds()                   # Apaga todos los LEDs
    led_pins[sequence_step].value(1)      # Enciende el LED en el índice actual
    sequence_step += 1                    # Incrementa el paso
    if sequence_step >= len(led_pins):    # Si llega al final de la lista
        sequence_step = 0                 # Vuelve al inicio

# Enciende un LED de derecha a izquierda en cada llamada
def next_step_der_izq():
    global sequence_step
    turn_off_all_leds()
    # Usa `len - 1 - step` para ir del último al primer pin
    led_pins[len(led_pins) - 1 - sequence_step].value(1) 
    sequence_step += 1
    if sequence_step >= len(led_pins):
        sequence_step = 0
    
# Mueve LEDs desde el centro hacia los extremos
def next_step_centros_extremos():
    global sequence_step
    turn_off_all_leds()
    num_pairs = len(led_pins) // 2        # Calcula la mitad de los LEDs
    led_pins[num_pairs - 1 - sequence_step].value(1) # Enciende el pin del lado izquierdo
    led_pins[num_pairs + sequence_step].value(1)     # Enciende el pin del lado derecho
    sequence_step += 1
    if sequence_step >= num_pairs:        # Si se completó el recorrido
        sequence_step = 0

# Mueve LEDs desde los extremos hacia el centro
def next_step_extremos_centros():
    global sequence_step
    turn_off_all_leds()
    num_pairs = len(led_pins) // 2
    led_pins[sequence_step].value(1)                  # Enciende el pin del lado izquierdo
    led_pins[len(led_pins) - 1 - sequence_step].value(1) # Enciende el pin del lado derecho
    sequence_step += 1
    if sequence_step >= num_pairs:
        sequence_step = 0

# Simula el movimiento de una barra de volumen
def next_step_vumetro():
    global sequence_step
    turn_off_all_leds()
    if sequence_step < len(led_pins):     # Enciende los LEDs hacia adelante
        for i in range(sequence_step + 1):
            led_pins[i].value(1)
    else:                                 # Apaga los LEDs hacia atrás
        for i in range(len(led_pins) - 1, sequence_step - len(led_pins) - 1, -1):
            led_pins[i].value(0)
    
    sequence_step += 1
    if sequence_step >= 2 * len(led_pins): # Vuelve a empezar cuando termina el ciclo completo
        sequence_step = 0

# Enciende solo los LEDs en posiciones pares
def next_step_pares():
    turn_off_all_leds()
    for i in range(1, len(led_pins), 2):  # Recorre los índices 1, 3, 5, etc.
        led_pins[i].value(1)
    
# Enciende solo los LEDs en posiciones impares
def next_step_nones():
    turn_off_all_leds()
    for i in range(0, len(led_pins), 2):  # Recorre los índices 0, 2, 4, etc.
        led_pins[i].value(1)

# Parpadea todos los LEDs
def next_step_opcional():
    global sequence_step
    if sequence_step % 2 == 0:            # Si el paso es par, enciende todos los LEDs
        for pin in led_pins:
            pin.value(1)
    else:                                 # Si es impar, apaga todos
        for pin in led_pins:
            pin.value(0)
    sequence_step += 1
    if sequence_step >= 2:                # Vuelve a empezar
        turn_off_all_leds()
        sequence_step = 0
        
# Mapea las claves (teclas) de la página web a las funciones de secuencia
sequences = {
    '1': next_step_izq_der,
    '2': next_step_der_izq,
    '3': next_step_centros_extremos,
    '4': next_step_extremos_centros,
    '5': next_step_vumetro,
    '6': next_step_pares,
    '7': next_step_nones,
    '8': next_step_opcional,
}

# La función que se llama cuando se recibe un comando del navegador
def control_leds(key_value):
    global current_sequence_name, sequence_step, last_step_time
    
    # Reinicia el estado de la secuencia
    sequence_step = 0
    last_step_time = time.ticks_ms()
    
    if key_value == '9':                  # Si el comando es '9', apaga los LEDs
        print("Tecla 9 recibida. Apagando todos los LEDs.")
        current_sequence_name = None
        turn_off_all_leds()
        return "Todos los LEDs apagados."
    
    if key_value in sequences:            # Si el comando está en la lista de secuencias
        print(f"Tecla {key_value} recibida. Iniciando secuencia.")
        current_sequence_name = key_value # Asigna la nueva secuencia
        return f"Secuencia {key_value} iniciada."
    else:                                 # Si el comando no es válido
        print(f"Tecla {key_value} no reconocida.")
        return "Comando no válido."

# Inicia el servidor web
def start_server():
    global last_step_time
    wlan = connect_to_wifi()              # Se conecta a la red WiFi
    if not wlan:
        return

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crea un objeto de socket TCP
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permite reutilizar la dirección del puerto
    s.bind(('', 80))                      # Asocia el socket al puerto 80
    s.listen(5)                           # Pone el socket en modo de escucha
    s.setblocking(False)                  # Configura el socket para que no se "congele" esperando
    print('Servidor escuchando en el puerto 80')
    last_step_time = time.ticks_ms()      # Guarda el tiempo de inicio

    while True:                           # El bucle principal del programa
        # Intenta aceptar una conexión, pero no se bloquea si no hay
        try:
            conn, addr = s.accept()         # Acepta una nueva conexión
            # El socket de conexión (conn) se configura con un tiempo de espera
            conn.settimeout(2.0)
            request = conn.recv(1024).decode('utf-8') # Lee la petición HTTP del navegador
            
            key_value = None
            if 'GET /control' in request:   # Busca el comando en la URL de la petición
                query_start = request.find('key=') + 4
                if query_start > 3:
                    query_end = request.find(' ', query_start)
                    key_value = request[query_start:query_end] # Extrae el valor de la tecla

            response_message = "Comando no reconocido."
            if key_value:
                response_message = control_leds(key_value) # Llama a la función de control

            response_data = json.dumps({"message": response_message})
            response = f"HTTP/1.1 200 OK\r\nAccess-Control-Allow-Origin: *\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{response_data}"
            
            conn.send(response.encode('utf-8')) # Envía la respuesta al navegador
            conn.close()                       # Cierra la conexión
            print('Respuesta enviada.')
        except OSError:
            # Si no hay peticiones de conexión, simplemente continúa sin bloquearse
            pass

        # Ejecuta el siguiente paso de la secuencia si ha pasado el tiempo de retraso
        current_time = time.ticks_ms()
        if current_sequence_name and time.ticks_diff(current_time, last_step_time) > step_delay:
            sequences[current_sequence_name]() # Llama a la función de la secuencia
            last_step_time = current_time      # Actualiza el tiempo del último paso
            
        # Pequeña pausa para no sobrecargar el procesador del Pico
        time.sleep(0.005)


start_server()
