# AC-Alerter

Monitor de actualizaciones para notas de la cátedra de Arquitectura de Computadoras y SIU Guaraní.

## Requisitos Previos

1. Python 3.7 o superior
2. Brave Browser instalado en el sistema
   - Windows: Descarga e instala desde https://brave.com/download/
   - Linux (Ubuntu/Debian):
     ```bash
     sudo apt install curl
     sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg
     echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main"|sudo tee /etc/apt/sources.list.d/brave-browser-release.list
     sudo apt update
     sudo apt install brave-browser
     ```

## Configuración

1. Crea un entorno virtual de Python:
```bash
python -m venv venv
```

2. Activa el entorno virtual:
- Windows:
```bash
.\venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Copia el archivo `.env.example` a `.env` y configura tus credenciales:
```bash
cp .env.example .env
```

5. Edita el archivo `.env` y agrega tus credenciales de SIU Guaraní:
```
SIU_GUARANI_USER=tu_usuario
SIU_GUARANI_PASSWORD=tu_contraseña
```

## Solución de Problemas

Si encuentras errores relacionados con el WebDriver:

1. Asegúrate de que Brave Browser esté instalado y actualizado
2. Verifica que el PATH del sistema incluya la ubicación de Brave
3. Si el error persiste, intenta:
   - Desinstalar y reinstalar Brave
   - Limpiar la caché del navegador
   - Eliminar la carpeta `.wdm` en tu directorio de usuario si existe

Las ubicaciones típicas de Brave son:
- Windows: `%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe`
- Linux: `/usr/bin/brave` o `/usr/bin/brave-browser`
- Mac: `/Applications/Brave Browser.app/Contents/MacOS/Brave Browser`

## Uso

Para iniciar el monitor:

```bash
python monitor.py
```

El script realizará las siguientes acciones:
- Monitoreará la página de la cátedra en busca de actualizaciones
- Iniciará sesión en SIU Guaraní y verificará si hay notas nuevas
- Mostrará notificaciones de Windows cuando detecte cambios
- Registrará toda la actividad en el archivo `monitor.log`

El monitor verificará ambos sistemas cada 5 minutos. Puedes modificar este intervalo cambiando la constante `CHECK_INTERVAL_MINUTES` en el archivo `monitor.py`.

## Estructura del Proyecto

```
.
├── .env.example          # Plantilla para configuración
├── .env                  # Configuración (crear a partir de .env.example)
├── monitor.py           # Script principal unificado
├── monitor.log          # Archivo de registro
├── requirements.txt     # Dependencias del proyecto
└── README.md           # Este archivo
```

## Logs

El script genera logs detallados en el archivo `monitor.log`. Puedes consultar este archivo para ver el historial de verificaciones y cualquier error que pueda ocurrir.

## Detener el Monitor

Para detener el monitor, presiona `Ctrl+C` en la terminal donde está ejecutándose. 