# Controlador de LEDs con Raspberry Pi Pico W y Servidor Web

Este proyecto utiliza una Raspberry Pi Pico W para controlar 8 LEDs a través de una interfaz web moderna y responsiva. El servidor web está alojado en la propia Pico W, permitiendo el control desde cualquier dispositivo (teléfono, tablet, computadora) conectado a la misma red local.



## 🚀 Características Principales

* **Control Remoto vía WiFi**: Maneja los LEDs sin necesidad de conexión física al ordenador.
* **Interfaz Web Intuitiva**: Un teclado numérico permite seleccionar entre 8 secuencias de luces predefinidas y detener la animación (tecla 9).
* **Servidor Asíncrono**: El código está diseñado para manejar peticiones web sin detener las secuencias de LEDs en ejecución.
* **Autocontenido**: Tanto el backend (MicroPython) como el frontend (HTML/CSS/JS) residen en la memoria de la Pico W.

---

## 🛠️ Hardware y Software Necesario

### Hardware
* Raspberry Pi Pico W
* 8 LEDs (cualquier color)
* Protoboard y cables de conexión (Jumpers)
* 8 Resistencias de 220Ω (una para cada LED)

### Software
* [Thonny IDE](https://thonny.org/): Recomendado para programar y transferir archivos a la Pico.
* [Visual studio code]
* [Firmware de MicroPython para Pico W](https://micropython.org/download/rp2-pico-w/): Necesario para ejecutar el código Python en la placa.

---

## ⚙️ Cómo Funciona el Proyecto

El sistema se divide en dos componentes principales que se comunican entre sí:

1.  **Backend (`main.py` en MicroPython)**: Es el cerebro del proyecto. Se encarga de:
    * Conectarse a la red WiFi y obtener una dirección IP.
    * Iniciar un servidor web en el puerto 80.
    * Escuchar peticiones entrantes y distinguir si se está pidiendo la página web (`/`) o un comando de control (`/control`).
    * Ejecutar un bucle infinito que actualiza el estado de los LEDs según la secuencia seleccionada.

2.  **Frontend (`index.html`)**: Es la interfaz de usuario que se ejecuta en el navegador.
    * Presenta una botonera (keypad) de 3x3.
    * Utiliza **JavaScript** para capturar los clics en los botones.
    * Envía los comandos al backend usando la **API Fetch**, enviando peticiones a URLs relativas como `/control?key=1`.

El flujo de interacción es el siguiente:
1.  El usuario accede a la IP de la Pico desde su teléfono.
2.  El servidor en la Pico responde enviando el archivo `index.html`.
3.  El navegador del usuario renderiza la página con el teclado numérico.
4.  Al presionar un botón, el JavaScript envía un comando al servidor.
5.  El servidor en la Pico recibe el comando, actualiza su variable de estado (qué secuencia ejecutar) y envía una respuesta JSON de confirmación.
6.  El bucle principal de la Pico lee esta variable de estado y controla los pines GPIO para crear la animación visual en los LEDs.

---

## 📂 Análisis del Código

### `main.py` (Backend en MicroPython)

El código se organiza en las siguientes partes:

* **Configuración Inicial**: Se importan las librerías, se definen las credenciales WiFi, se inicializan los 8 pines de los LEDs y se declaran las variables globales de estado (`current_sequence_name`, `sequence_step`, etc.), que actúan como la memoria del programa.

* **Funciones de Secuencia (`next_step_*`)**: Cada una de estas funciones es un "fotograma" de una animación. No ejecutan la animación completa, sino que definen qué LEDs deben estar encendidos en un único paso. El bucle principal las llama repetidamente para crear el efecto de movimiento.

* **Controlador de Comandos (`control_leds`)**: Esta función recibe la "tecla" presionada desde la web. Su única tarea es actualizar la variable global `current_sequence_name` para indicarle al bucle principal qué nueva animación debe comenzar.

* **Servidor Web (`start_server`)**: Es el corazón del programa. Contiene un bucle infinito `while True` que realiza dos tareas:
    1.  **Atender Peticiones**: Usa un bloque `try/except` para aceptar conexiones web de forma no bloqueante. Analiza la URL solicitada para determinar si se debe servir el `index.html` o procesar un comando de `/control`.
    2.  **Animar LEDs**: Revisa constantemente si hay una secuencia activa y si ha transcurrido el tiempo (`step_delay`) desde el último paso. Si es así, ejecuta la función de secuencia correspondiente.

### `index.html` (Frontend)

Este archivo contiene tres lenguajes:

* **HTML**: Define la estructura de la página: un contenedor principal, una cabecera y una rejilla (`keypad`) para los botones. Se usan atributos `data-key` para identificar cada botón numérico.

* **CSS**: Se encuentra dentro de la etiqueta `<style>` y se encarga de todo el aspecto visual. Define el tema oscuro, el diseño de la botonera y los efectos al presionar un botón (`:active`).

* **JavaScript**: Está dentro de la etiqueta `<script>` y añade toda la interactividad:
    * `addEventListener`: Se asignan escuchadores de eventos a todos los botones para detectar el evento `click`.
    * `async function sendStatus(url)`: Es la función clave de comunicación. Utiliza `fetch()` para enviar la petición al servidor de la Pico de forma asíncrona. El uso de **URLs relativas** es crucial, ya que evita tener que escribir la IP de la Pico en el código, haciéndolo más robusto y portable.

---

## ⚠️ Dificultades y Soluciones durante el Desarrollo

1.  **Problema: Servidor Bloqueante.**
    * **Dificultad**: Un servidor web simple se queda "congelado" esperando una conexión (`socket.accept()`), lo que detendría por completo las animaciones de los LEDs.
    * **Solución**: Se implementó un servidor **no bloqueante** configurando el socket con `s.setblocking(False)` y envolviendo la lógica de aceptación de conexiones en un bloque `try...except OSError`. Esto permite que el bucle principal continúe ejecutándose y animando los LEDs, incluso si no hay peticiones web.

2.  **Problema: IP Dinámica.**
    * **Dificultad**: La dirección IP de la Pico puede cambiar, lo que obligaría a modificar el código JavaScript constantemente si la IP estuviera escrita directamente en él.
    * **Solución**: El problema se resolvió al **alojar el archivo `index.html` en la propia Pico**. Esto permite que el JavaScript use **URLs relativas** (ej. `/control?key=1`). El navegador automáticamente envía la petición a la misma IP desde la que se cargó la página, eliminando la necesidad de conocer la IP de antemano.

3.  **Problema: Gestión de Estado.**
    * **Dificultad**: El servidor necesita una forma de "recordar" qué secuencia se está ejecutando, separando la lógica de recepción de comandos de la lógica de animación.
    * **Solución**: Se utilizó la variable global `current_sequence_name` en MicroPython como una máquina de estados simple. La sección del servidor que maneja las peticiones web se encarga de *escribir* en esta variable, mientras que la sección del bucle que anima los LEDs se encarga de *leerla* en cada ciclo para actuar en consecuencia.