# Requisitos del sistema

## Requisitos Funcionales (RF):

| N | Requisito | Descripción | Criterio de Aceptación |
|---|---|---|---|
| RF-01 | Búsqueda de recurso | El solicitante filtra recursos por tipo, fecha y bloque horario, visualizando solo los que están disponibles. | **Dado** un tipo de recurso, fecha y bloque horario, **cuando** el usuario busca, **entonces** el sistema lista únicamente los recursos libres para ese bloque. El sistema rechaza fechas anteriores al día actual y no muestra resultados para ellas. |
| RF-02 | Reserva de recurso | El solicitante confirma la reserva de un recurso disponible para un bloque específico. | **Dado** un recurso libre seleccionado, **cuando** el usuario confirma la reserva, **entonces** el sistema registra la reserva y bloquea el recurso para otros usuarios en ese horario. La confirmación se rechaza si la fecha es anterior al día actual. |
| RF-03 | Generación de comprobante (QR) | El sistema emite un código QR digital con el ID único y datos de la reserva confirmada. | **Dado** una reserva confirmada exitosamente, **cuando** se procesa la confirmación, **entonces** el sistema muestra en pantalla un código QR legible con el ID de la reserva. |
| RF-04 | Validación de entrega (check-in) | El bibliotecario escanea/valida el código QR al presentarse el solicitante, cambiando el estado a "En Uso". | **Dado** un QR de reserva válida para el horario actual, **cuando** el bibliotecario lo valida, **entonces** la reserva cambia a estado "En Uso". El panel muestra el estado del inventario del día (disponible, reservado, en uso, no disponible) por recurso y bloque. |
| RF-05 | Registro de devolución (check-out) | El bibliotecario valida la recepción del recurso mediante el código QR, liberándolo a estado "Disponible". | **Dado** un recurso en estado "En Uso", **cuando** el bibliotecario valida el QR de devolución, **entonces** la reserva cambia a "Finalizada" y el recurso queda libre. |
| RF-06 | Control de tope de reservas | El sistema restringe a un máximo de 2 reservas activas diarias por usuario para evitar el acaparamiento. | **Dado** un usuario con 2 reservas activas en el mismo día, **cuando** intenta crear una 3ª reserva para esa fecha, **entonces** el sistema rechaza la solicitud con mensaje explicativo. |
| RF-07 | Gestión de penalizaciones por retraso | El sistema bloquea temporalmente (7 días) a los usuarios que entregan recursos fuera del horario pactado. | **Dado** un recurso devuelto con posterioridad al término del bloque, **cuando** se registra la devolución, **entonces** el usuario pasa a estado "Sancionado" por 7 días sin poder reservar. |
| RF-08 | Autenticación y roles básicos | Identificación diferenciada entre Solicitante (estudiante/docente) y Resolutor (bibliotecario). | **Dado** un usuario ingresando sus credenciales ficticias, **cuando** inicia sesión, **entonces** el sistema carga la vista correspondiente a su rol (solicitante o bibliotecario). |

## Requisitos No Funcionales (RNF):

| N | Requisito | Métrica y Umbral | Método de Verificación |
|---|---|---|---|
| RNF-01 | Rendimiento en reserva y QR | Tiempo de respuesta <= 1,5 seg. en confirmar reserva y emitir QR. | Medición mediante script/curl con promedio de 20 peticiones concurrentes. |
| RNF-02 | Usabilidad y diseño responsivo | Adaptación correcta en `viewport` móvil (360px) y escritorio (1280px) sin scroll horizontal ni textos cortados. | Inspección de layout en `DevTools` en 3 resoluciones y auditoría `Lighthouse` accesibilidad >= 90. |
| RNF-03 | Seguridad de datos | Cero credenciales ni datos personales reales; contraseñas almacenadas mediante hash. | Revisión de estructura de datos ficticios y verificación de exclusión en `.gitignore`. |
