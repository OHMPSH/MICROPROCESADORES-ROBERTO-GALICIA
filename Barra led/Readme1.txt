
Proyecto: Controlador de LEDs con Interfaz Web
Este repositorio contiene el código para controlar una tira de 8 LEDs mediante una interfaz web. Se presentan dos versiones diferentes del proyecto: una para ejecutarse directamente en una Raspberry Pi Pico W y otra para visualizar la interfaz localmente en una PC.

📁 Opción 1: Servidor en la Pico W (Versión Completa)
Esta carpeta (/pico_w_servidor) contiene la versión principal y completamente funcional del proyecto. El código de MicroPython convierte la Raspberry Pi Pico W en un servidor web que aloja la interfaz de control.

Uso
Abre el archivo main.py y modifica las credenciales de tu red WiFi (ssid y password).

Conecta tu Pico W y sube los archivos main.py y index.html a su memoria raíz usando Thonny IDE.

Ejecuta el script main.py en la Pico. La consola de Thonny te mostrará la dirección IP asignada.

Desde un dispositivo (teléfono o PC) conectado a la misma red WiFi, abre un navegador web y accede a esa dirección IP.

Usa la interfaz para controlar las secuencias de LEDs en tiempo real.

Esta es la versión funcional que controla el hardware.

💻 Opción 2: Prueba Local en PC (Solo Interfaz Visual)
Esta carpeta (/pc_interfaz_local) contiene únicamente el archivo index.html para una rápida visualización del frontend en cualquier computadora.

Uso
Abre la carpeta en tu explorador de archivos.

Haz doble clic en el archivo index.html para abrirlo con tu navegador web preferido (Chrome, Firefox, etc.).

Nota Importante: Esta versión es solo para fines visuales. Te permite ver y interactuar con la interfaz, pero no controlará ningún LED, ya que no está conectada al servidor de la Raspberry Pi Pico W. Verás errores en la consola del navegador al presionar los botones, lo cual es normal.