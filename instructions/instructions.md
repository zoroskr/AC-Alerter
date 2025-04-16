#Project Overview

Este proyecto consiste en scrapear distintas paginas con el objetivo de saber si subieron las notas de mi evaluacion.

#TO-DO

Necesito que "monitor_siu_guarani.py" sea un script que ingrese a https://autogestion.guarani.unlp.edu.ar/ (es el login de la pagina), se deben ingresar mis credenciales que estaran en el .env. Estos son los inputs asociados

<input id="usuario" name="usuario" type="text" value="" maxlength="60"> (para el nombre de usuario)

<input id="password" name="password" type="password" value="" maxlength="20"> (para la contraseña)

<input id="login" name="login" type="submit" value="Ingresar" class="btn btn-info"> (boton para iniciar sesion)

Una vez que se inicio sesion se debe ir a https://autogestion.guarani.unlp.edu.ar/acceso/cambiar_carrera?id=477&op=actuacion_provisoria


Actualmente hay 3 de estos:

 <div class="alert"> No hay información sobre actuaciones provisorias en  promociones </div>

 Si se detecta que no hay 3 significa que subieron mi nota asi que se debe generar una alerta mediante las alertas de windows. 

Puedes unificar monitor_siu_guarani con monitor_catedra, ya que ambos scripts sirven para detectar lo mismo o si lo ves necesario puedo ejecutarlos de forma separada. 


# Project Structure

Directorios:
•  instructions/: Contiene documentación
•  venv/: El entorno virtual de Python

Archivos principales:
•  monitor_catedra.py: Script principal para monitorear cátedra
•  monitor_siu_guarani.py: Script principal para monitorear SIU Guaraní
•  test_notifications.py: Script para pruebas de notificaciones
•  requirements.txt: Lista de dependencias del proyecto
•  README.md: Documentación principal del proyecto

Archivos de datos/configuración:
•  .gitignore: Configuración de Git
•  last_update_timestamp.txt: Archivo para seguimiento de actualizaciones
•  monitor.log: Archivo de registro
•  pagina_actual.html: Archivo temporal/caché de página web