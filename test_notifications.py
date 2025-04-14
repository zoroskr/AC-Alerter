from plyer import notification

def test_notification():
    notification.notify(
        title="Prueba de Notificación",
        message="Si puedes ver esto, las notificaciones están funcionando correctamente!",
        app_name="Monitor Cátedra",
        timeout=10
    )

if __name__ == "__main__":
    print("Enviando notificación de prueba...")
    test_notification()
    print("Si no viste la notificación, verifica que las notificaciones de Windows estén habilitadas") 