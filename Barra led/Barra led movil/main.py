# main.py para Raspberry Pi Pico W
# Importa las librerías necesarias
import network    # Permite la conexión a redes WiFi
import socket     # Para crear un servidor web y manejar conexiones de red
import time       # Para controlar el tiempo, como los retrasos entre pasos
from machine import Pin    # Para controlar los pines del microcontrolador
import json       # Para trabajar con datos en formato JSON

# Define el pin del LED integrado de la placa como salida
led_onboard = Pin("LED", Pin.OUT)

# Configuración de tu red WiFi
ssid = 'Totalplay-2.4G-5a18'
password = 'B4A9wGff5PJX49xc'

# Configuración de los pines de los LEDs que se van a usar, en una lista
led_pins = [Pin(16, Pin.OUT), Pin(17, Pin.OUT), Pin(18, Pin.OUT), Pin(19, Pin.OUT),
            Pin(20, Pin.OUT), Pin(21, Pin.OUT), Pin(22, Pin.OUT), Pin(26, Pin.OUT)]

# Variables globales que definen el estado actual de la "máquina de estados"
current_sequence_name = None  
sequence_step = 0            
last_step_time = 0           
step_delay = 100             

# Conectar a la red WiFi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF) 
    wlan.active(True)                   
    print("Conectando a la red:", ssid)
    led_onboard.value(1)                  
    wlan.connect(ssid, password)          
    
    max_attempts = 15                   
    attempts = 0                        
    while not wlan.isconnected() and attempts < max_attempts: 
        print('.', end='')              
        time.sleep(1)                   
        attempts += 1                   

    if wlan.isconnected():                
        print('\nConexión exitosa. Dirección IP:', wlan.ifconfig()[0]) 
        return wlan                       
    else:                                 
        print('\nFallo la conexión a la red. Revisa el SSID y la contraseña.')
        led_onboard.value(0)            
        return None

# Función para apagar todos los LEDs en la lista `led_pins`
def turn_off_all_leds():
    for pin in led_pins:                
        pin.value(0)                  
    print("Todos los LEDs están apagados.")
    
# --- Funciones de Secuencia de LEDs (un solo paso) ---
def next_step_izq_der():
    global sequence_step
    turn_off_all_leds()
    led_pins[sequence_step].value(1)
    sequence_step += 1
    if sequence_step >= len(led_pins):
        sequence_step = 0

def next_step_der_izq():
    global sequence_step
    turn_off_all_leds()
    led_pins[len(led_pins) - 1 - sequence_step].value(1)
    sequence_step += 1
    if sequence_step >= len(led_pins):
        sequence_step = 0
    
def next_step_centros_extremos():
    global sequence_step
    turn_off_all_leds()
    num_pairs = len(led_pins) // 2
    led_pins[num_pairs - 1 - sequence_step].value(1)
    led_pins[num_pairs + sequence_step].value(1)
    sequence_step += 1
    if sequence_step >= num_pairs:
        sequence_step = 0

def next_step_extremos_centros():
    global sequence_step
    turn_off_all_leds()
    num_pairs = len(led_pins) // 2
    led_pins[sequence_step].value(1)
    led_pins[len(led_pins) - 1 - sequence_step].value(1)
    sequence_step += 1
    if sequence_step >= num_pairs:
        sequence_step = 0

def next_step_vumetro():
    global sequence_step
    turn_off_all_leds()
    if sequence_step < len(led_pins):
        for i in range(sequence_step + 1):
            led_pins[i].value(1)
    else:
        for i in range(len(led_pins) - 1, sequence_step - len(led_pins) - 1, -1):
            led_pins[i].value(0)
    
    sequence_step += 1
    if sequence_step >= 2 * len(led_pins):
        sequence_step = 0

def next_step_pares():
    turn_off_all_leds()
    for i in range(1, len(led_pins), 2):
        led_pins[i].value(1)
    
def next_step_nones():
    turn_off_all_leds()
    for i in range(0, len(led_pins), 2):
        led_pins[i].value(1)

def next_step_opcional():
    global sequence_step
    if sequence_step % 2 == 0:
        for pin in led_pins:
            pin.value(1)
    else:
        for pin in led_pins:
            pin.value(0)
    sequence_step += 1
    if sequence_step >= 2:
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
    
    sequence_step = 0
    last_step_time = time.ticks_ms()
    
    if key_value == '9':
        print("Tecla 9 recibida. Apagando todos los LEDs.")
        current_sequence_name = None
        turn_off_all_leds()
        return "Todos los LEDs apagados."
    
    if key_value in sequences:
        print(f"Tecla {key_value} recibida. Iniciando secuencia.")
        current_sequence_name = key_value
        return f"Secuencia {key_value} iniciada."
    else:
        print(f"Tecla {key_value} no reconocida.")
        return "Comando no válido."

# Inicia el servidor web
def start_server():
    global last_step_time
    wlan = connect_to_wifi()
    if not wlan:
        return

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))
    s.listen(5)
    s.setblocking(False)
    print('Servidor escuchando en el puerto 80')
    last_step_time = time.ticks_ms()

    while True:
        try:
            conn, addr = s.accept()
            conn.settimeout(2.0)
            request = conn.recv(1024).decode('utf-8')
            print('Petición recibida:', request.split('\r\n')[0])
            
            # Si la petición es para la página principal (la IP sin nada más)
            if 'GET / ' in request:
                try:
                    with open('index.html', 'r') as file:
                        html_content = file.read()
                    response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n' + html_content
                    conn.send(response.encode('utf-8'))
                    conn.close()
                    print('Página web enviada.')
                    continue
                except OSError as e:
                    print(f'Error al leer index.html: {e}')
                    response_data = json.dumps({"message": "Error del servidor: No se encuentra index.html"})
                    response = f"HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{response_data}"
                    conn.send(response.encode('utf-8'))
                    conn.close()
                    continue

            key_value = None
            if 'GET /control' in request:
                query_start = request.find('key=') + 4
                if query_start > 3:
                    query_end = request.find(' ', query_start)
                    key_value = request[query_start:query_end]

            response_message = "Comando no reconocido."
            if key_value:
                response_message = control_leds(key_value)
            
            response_data = json.dumps({"message": response_message})
            response = f"HTTP/1.1 200 OK\r\nAccess-Control-Allow-Origin: *\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{response_data}"
            
            conn.send(response.encode('utf-8'))
            conn.close()
            print('Respuesta enviada.')
        except OSError as e:
            if e.args[0] == 11:
                pass
            else:
                pass

        current_time = time.ticks_ms()
        if current_sequence_name and time.ticks_diff(current_time, last_step_time) > step_delay:
            sequences[current_sequence_name]()
            last_step_time = current_time
            
        time.sleep(0.005)

start_server()