# Monitor de Actualización de Cátedra

Este script monitorea la página web de la cátedra de Arquitectura de Computadoras para detectar cambios en la fecha de última actualización.

## Requisitos

- Python 3.x
- Las dependencias listadas en `requirements.txt`

## Instalación

1. Clona o descarga este repositorio
2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Ejecución Normal
Para ejecutar el monitor con una ventana de consola visible:
```bash
python monitor_catedra.py
```

### Ejecución en Segundo Plano
Para ejecutar el monitor sin ventana de consola visible:
1. Renombra el archivo a `monitor_catedra.pyw`
2. Haz doble clic en el archivo

## Funcionamiento

- El script verifica la página cada 5 minutos
- Cuando detecta un cambio en la fecha de última actualización, muestra una notificación de escritorio
- Los logs se guardan en `monitor.log`
- El estado se guarda en `last_update_timestamp.txt`

## Configuración

Puedes modificar las siguientes constantes en el archivo `monitor_catedra.py`:
- `URL`: La dirección de la página a monitorear
- `CHECK_INTERVAL_MINUTES`: Intervalo de verificación en minutos
- `STATE_FILE`: Nombre del archivo para guardar el estado

## Notas

- El script requiere conexión a internet para funcionar
- Las notificaciones funcionan en Windows
- Para detener el script, presiona Ctrl+C en la ventana de consola (si está visible) 