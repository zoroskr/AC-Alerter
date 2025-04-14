import requests
from bs4 import BeautifulSoup
from plyer import notification
import time
import schedule
import os
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)

# Constantes
URL = "http://163.10.22.92/catedras/arquitecturaP2003/"
CHECK_INTERVAL_MINUTES = 5
STATE_FILE = "last_update_timestamp.txt"
last_known_timestamp = None

def workspace_html(url):
    """Obtiene el contenido HTML de la URL dada."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Imprimir información de la respuesta
        logging.info(f"Código de estado HTTP: {response.status_code}")
        logging.info(f"Headers de respuesta: {dict(response.headers)}")
        
        # Guardar el contenido HTML en un archivo para inspección
        with open('pagina_actual.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        logging.info("Contenido HTML guardado en 'pagina_actual.html'")
        
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al obtener la página: {e}")
        return None

def extract_timestamp(html_content):
    """Extrae la fecha y hora del elemento span dentro del li específico."""
    if html_content is None:
        return None
    
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Imprimir todos los elementos li para depuración
        logging.info("Buscando elementos li en la página:")
        for li in soup.find_all('li'):
            logging.info(f"Elemento li encontrado: {li.text.strip()}")
        
        # Buscar todos los elementos span que contengan un timestamp
        spans = soup.find_all('span')
        for span in spans:
            text = span.text.strip()
            # Verificar si el texto tiene el formato de fecha esperado (YYYY-MM-DD HH:MM:SS)
            if len(text) == 19 and text[4] == '-' and text[7] == '-' and text[10] == ' ' and text[13] == ':' and text[16] == ':':
                logging.info(f"Timestamp encontrado en span: {text}")
                return text
        
        # Si no encontramos por el formato, intentamos buscar por el texto del li padre
        for li in soup.find_all('li'):
            if 'actualización' in li.text.lower():
                span = li.find('span')
                if span:
                    timestamp = span.text.strip()
                    logging.info(f"Timestamp encontrado en li con 'actualización': {timestamp}")
                    return timestamp
        
        logging.warning("No se encontró ningún timestamp en la página")
        # Imprimir el HTML completo para depuración
        logging.info("Contenido HTML completo:")
        logging.info(html_content)
        
        return None
    except Exception as e:
        logging.error(f"Error al extraer el timestamp: {e}")
        return None

def show_notification(title, message):
    """Muestra una notificación de escritorio en Windows."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Monitor Cátedra",
            timeout=10
        )
    except Exception as e:
        logging.error(f"Error al mostrar la notificación: {e}")

def load_last_timestamp(filename):
    """Lee la última fecha conocida desde el archivo de estado."""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return f.read().strip()
        return None
    except IOError as e:
        logging.error(f"Error al leer el archivo de estado: {e}")
        return None

def save_last_timestamp(filename, timestamp):
    """Guarda la nueva fecha conocida en el archivo de estado."""
    try:
        with open(filename, 'w') as f:
            f.write(timestamp)
    except IOError as e:
        logging.error(f"Error al guardar el archivo de estado: {e}")

def check_for_update():
    """Orquesta el proceso de chequeo."""
    global last_known_timestamp
    
    logging.info(f"Verificando actualizaciones en: {URL}")
    html_content = workspace_html(URL)
    
    if html_content:
        logging.info("Contenido HTML obtenido correctamente")
        current_timestamp = extract_timestamp(html_content)
        
        if current_timestamp:
            if last_known_timestamp is not None and current_timestamp != last_known_timestamp:
                logging.info(f"¡Cambio detectado! Nueva fecha: {current_timestamp}")
                show_notification(
                    "Actualización Detectada",
                    f"La página de la cátedra se actualizó a las: {current_timestamp}"
                )
            else:
                logging.info(f"No se detectaron cambios. Timestamp actual: {current_timestamp}")
            
            last_known_timestamp = current_timestamp
            save_last_timestamp(STATE_FILE, current_timestamp)
            logging.info(f"Última actualización conocida: {current_timestamp}")
        else:
            logging.error("No se pudo extraer el timestamp de la página")
    else:
        logging.error("No se pudo obtener el contenido HTML de la página")

def test_notification():
    """Función para probar las notificaciones de Windows."""
    try:
        notification.notify(
            title="Prueba de Notificación",
            message="Si puedes ver esto, las notificaciones están funcionando correctamente!",
            app_name="Monitor Cátedra",
            timeout=10
        )
        logging.info("Notificación de prueba enviada")
    except Exception as e:
        logging.error(f"Error al mostrar la notificación de prueba: {e}")

if __name__ == "__main__":
    # Probar las notificaciones al inicio
    test_notification()
    
    # Cargar el estado inicial
    last_known_timestamp = load_last_timestamp(STATE_FILE)
    logging.info(f"Iniciando monitor... Última fecha conocida: {last_known_timestamp or 'Ninguna'}")
    
    # Programar la tarea
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_for_update)
    
    # Ejecutar una vez inmediatamente
    check_for_update()
    
    # Bucle principal
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Monitor detenido por el usuario")
            break
        except Exception as e:
            logging.error(f"Error inesperado: {e}")
            time.sleep(60)  # Esperar un minuto antes de reintentar 