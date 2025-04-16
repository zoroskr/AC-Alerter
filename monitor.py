import requests
from bs4 import BeautifulSoup
from plyer import notification
import time
import schedule
import os
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# Load environment variables
load_dotenv()

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
CATEDRA_URL = "http://163.10.22.92/catedras/arquitecturaP2003/"
GUARANI_LOGIN_URL = "https://autogestion.guarani.unlp.edu.ar/"
GUARANI_TARGET_URL = "https://autogestion.guarani.unlp.edu.ar/acceso/cambiar_carrera?id=477&op=actuacion_provisoria"
CHECK_INTERVAL_MINUTES = 8
STATE_FILE = "last_update_timestamp.txt"
last_known_timestamp = None
last_known_alerts_count = 3  # Initial count of alerts in SIU Guarani

def get_brave_path():
    """Obtiene la ruta al ejecutable de Brave según el sistema operativo."""
    if os.name == 'nt':  # Windows
        local_app_data = os.getenv('LOCALAPPDATA')
        brave_path = os.path.join(local_app_data, 'BraveSoftware', 'Brave-Browser', 'Application', 'brave.exe')
        if os.path.exists(brave_path):
            return brave_path
        # Intentar ruta alternativa para Windows
        program_files = os.getenv('PROGRAMFILES')
        brave_path = os.path.join(program_files, 'BraveSoftware', 'Brave-Browser', 'Application', 'brave.exe')
        if os.path.exists(brave_path):
            return brave_path
    
    logging.error("No se pudo encontrar el ejecutable de Brave")
    return None

def setup_selenium():
    """Configura y retorna una instancia de Brave WebDriver."""
    try:
        brave_path = get_brave_path()
        if not brave_path:
            raise Exception("No se pudo encontrar Brave Browser")

        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--log-level=3')  # Solo errores críticos
        chrome_options.add_argument('--headless')  # Ejecutar en modo headless (sin GUI)
        chrome_options.binary_location = brave_path

        try:
            service = Service()
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logging.error(f"Error al crear el servicio de Brave: {e}")
            # Intentar método alternativo
            logging.info("Intentando método alternativo de inicialización...")
            driver = webdriver.Chrome(options=chrome_options)
        
        driver.implicitly_wait(10)
        return driver
    except Exception as e:
        logging.error(f"Error al configurar Selenium con Brave: {e}")
        return None

def get_session():
    """Creates and returns a session with proper headers."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    return session

def login_to_guarani(driver):
    """Logs into SIU Guarani system using Selenium."""
    try:
        # Get credentials from environment variables
        username = os.getenv('SIU_GUARANI_USER')
        password = os.getenv('SIU_GUARANI_PASSWORD')

        if not username or not password:
            logging.error("Credenciales de SIU Guarani no encontradas en .env")
            return False

        # Navigate to login page
        driver.get(GUARANI_LOGIN_URL)
        
        # Esperar a que el formulario esté presente
        form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "guarani_form_login"))
        )
        
        # Esperar y llenar el campo de usuario
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='usuario']"))
        )
        username_input.clear()
        username_input.send_keys(username)
        logging.info("Usuario ingresado correctamente")
        
        # Esperar y llenar el campo de contraseña
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
        )
        password_input.clear()
        password_input.send_keys(password)
        logging.info("Contraseña ingresada correctamente")

        # Intentar diferentes métodos para enviar el formulario
        try:
            # Método 1: Encontrar y hacer click en el botón submit por su selector completo
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][name='login'][value='Ingresar']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(1)  # Dar tiempo para que el scroll termine
            submit_button.click()
            logging.info("Formulario enviado mediante click en botón submit")
        except Exception as e:
            logging.warning(f"Click en botón submit falló, intentando métodos alternativos: {e}")
            try:
                # Método 2: Enviar el formulario directamente
                driver.execute_script("""
                    document.querySelector('#guarani_form_login').submit();
                """)
                logging.info("Formulario enviado mediante JavaScript submit")
            except Exception as e:
                logging.warning(f"Submit mediante JavaScript falló, intentando último método: {e}")
                try:
                    # Método 3: Simular presionar Enter en el campo de contraseña
                    password_input.send_keys(Keys.RETURN)
                    logging.info("Formulario enviado mediante tecla Enter")
                except Exception as e:
                    logging.error(f"Todos los métodos de envío del formulario fallaron: {e}")
                    return False

        # Esperar a que la URL cambie y verificar que estamos en la página correcta
        time.sleep(5)  # Dar tiempo para que el formulario se procese
        
        try:
            WebDriverWait(driver, 15).until(
                lambda driver: "auth=form" not in driver.current_url and "acceso" not in driver.current_url
            )
            logging.info(f"Redirección exitosa. URL actual: {driver.current_url}")
        except TimeoutException:
            logging.error(f"Timeout esperando redirección. URL actual: {driver.current_url}")
            return False

        # Verificación final del login
        if "error" in driver.current_url.lower() or "acceso" in driver.current_url.lower():
            logging.error("Login a SIU Guarani falló - URL indica error o permanece en login")
            return False

        logging.info("Login a SIU Guarani exitoso")
        return True

    except Exception as e:
        logging.error(f"Error durante el login a SIU Guarani: {e}")
        driver.save_screenshot("error_login.png")  # Guardar screenshot en caso de error
        return False

def check_guarani_updates(driver):
    """Checks for updates in SIU Guarani system using Selenium."""
    global last_known_alerts_count
    logging.info("Verificando actualizaciones en SIU Guarani...")
    try:
        # Navigate to target page
        driver.get(GUARANI_TARGET_URL)
        

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert"))
        )
        
        # Mensajes específicos a buscar
        expected_messages = [
            "No hay información sobre actuaciones provisorias en cursadas",
            "No hay información sobre actuaciones provisorias en promociones",
            "No hay información sobre actuaciones provisorias en exámenes"
        ]
        
        # Get all alerts
        alerts = driver.find_elements(By.CLASS_NAME, "alert")
        
        # Contar cuántos de los mensajes esperados están presentes
        current_alerts_count = sum(
            1 for alert in alerts
            for message in expected_messages
            if message in alert.text
        )

        if current_alerts_count != last_known_alerts_count:
            if current_alerts_count < last_known_alerts_count:
                # Determinar qué tipo de actualización ocurrió
                missing_messages = [
                    msg for msg in expected_messages
                    if not any(msg in alert.text for alert in alerts)
                ]
                
                update_types = []
                for msg in missing_messages:
                    if "cursadas" in msg:
                        update_types.append("cursadas")
                    elif "promociones" in msg:
                        update_types.append("promociones")
                    elif "exámenes" in msg:
                        update_types.append("exámenes")
                
                update_message = f"Se detectaron cambios en: {', '.join(update_types)}"
                
                show_notification(
                    "¡Actualización en SIU Guarani!",
                    update_message
                )
                logging.info(f"Cambios detectados en SIU Guarani: {update_message}")
            last_known_alerts_count = current_alerts_count

        return True

    except (TimeoutException, WebDriverException) as e:
        logging.error(f"Error al verificar actualizaciones en SIU Guarani: {e}")
        return False

def workspace_html(url):
    """Obtiene el contenido HTML de la URL dada."""
    try:
        session = get_session()
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
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
        spans = soup.find_all('span')
        
        for span in spans:
            text = span.text.strip()
            if len(text) == 19 and text[4] == '-' and text[7] == '-' and text[10] == ' ' and text[13] == ':' and text[16] == ':':
                logging.info(f"Timestamp encontrado en span: {text}")
                return text
        
        for li in soup.find_all('li'):
            if 'actualización' in li.text.lower():
                span = li.find('span')
                if span:
                    timestamp = span.text.strip()
                    logging.info(f"Timestamp encontrado en li con 'actualización': {timestamp}")
                    return timestamp
        
        logging.warning("No se encontró ningún timestamp en la página")
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
            app_name="Monitor de Notas",
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

def check_catedra_update():
    """Verifica actualizaciones en la página de la cátedra."""
    global last_known_timestamp
    
    logging.info(f"Verificando actualizaciones en: {CATEDRA_URL}")
    html_content = workspace_html(CATEDRA_URL)
    
    if html_content:
        current_timestamp = extract_timestamp(html_content)
        
        if current_timestamp:
            if last_known_timestamp is not None and current_timestamp != last_known_timestamp:
                logging.info(f"¡Cambio detectado en cátedra! Nueva fecha: {current_timestamp}")
                show_notification(
                    "Actualización en Cátedra",
                    f"La página de la cátedra se actualizó a las: {current_timestamp}"
                )
            
            last_known_timestamp = current_timestamp
            save_last_timestamp(STATE_FILE, current_timestamp)
            logging.info(f"Última actualización conocida de cátedra: {current_timestamp}")
        else:
            logging.error("No se pudo extraer el timestamp de la página de cátedra")

def check_all_updates():
    """Verifica actualizaciones en ambos sistemas."""
    try:
        # Inicializar Selenium para esta verificación
        driver = setup_selenium()
        if not driver:
            logging.error("No se pudo inicializar el navegador. Saltando verificación de SIU Guarani.")
            check_catedra_update()
            return

        try:
            # Check SIU Guarani
            if login_to_guarani(driver):
                check_guarani_updates(driver)
        finally:
            # Asegurarnos de cerrar el navegador después de la verificación
            try:
                driver.quit()
                logging.info("Navegador cerrado correctamente")
            except Exception as e:
                logging.error(f"Error al cerrar el navegador: {e}")
        
        # Check Catedra (esto no usa Selenium)
        check_catedra_update()
        
    except Exception as e:
        logging.error(f"Error durante la verificación: {e}")

def test_notification():
    """Función para probar las notificaciones de Windows."""
    try:
        notification.notify(
            title="Prueba de Notificación",
            message="Si puedes ver esto, las notificaciones están funcionando correctamente!",
            app_name="Monitor de Notas",
            timeout=10
        )
        logging.info("Notificación de prueba enviada")
    except Exception as e:
        logging.error(f"Error al mostrar la notificación de prueba: {e}")

if __name__ == "__main__":
    try:
        # Probar las notificaciones al inicio
        test_notification()
        
        # Cargar el estado inicial
        last_known_timestamp = load_last_timestamp(STATE_FILE)
        logging.info(f"Iniciando monitor... Última fecha conocida de cátedra: {last_known_timestamp or 'Ninguna'}")
        
        # Programar la tarea de verificación
        schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_all_updates)
        
        # Ejecutar una vez inmediatamente
        check_all_updates()
        
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
    finally:
        # Ya no necesitamos cleanup_selenium() aquí porque el navegador se cierra después de cada verificación
        pass 