/* BibliotecaViva — mejoras de interfaz progresivas (sin frameworks).
 *
 * Ninguna acción depende de este archivo: los formularios funcionan con
 * JavaScript desactivado. Aquí solo se agregan comodidades de demostración.
 */
(function () {
  "use strict";

  /* Mostrar u ocultar la contraseña */
  document.querySelectorAll("[data-toggle-password]").forEach(function (button) {
    button.addEventListener("click", function () {
      var input = document.getElementById(
        button.getAttribute("data-toggle-password")
      );
      if (!input) {
        return;
      }
      var visible = input.type === "password";
      input.type = visible ? "text" : "password";
      button.setAttribute("aria-pressed", String(visible));
      button.setAttribute(
        "aria-label",
        visible ? "Ocultar contraseña" : "Mostrar contraseña"
      );
      var use = button.querySelector("use");
      if (use) {
        use.setAttribute("href", visible ? "#i-lock" : "#i-eye");
      }
    });
  });

  /* Envía el formulario solo si ya están completos los campos obligatorios,
   * para no mostrar errores mientras el usuario todavía está eligiendo. */
  function enviarSiCompleto(formulario) {
    if (formulario && formulario.checkValidity()) {
      formulario.submit();
    }
  }

  /* Actualizar los bloques disponibles al cambiar la fecha (RF-01) */
  var fecha = document.getElementById("id_fecha");
  var bloque = document.getElementById("id_bloque");
  var aviso = document.getElementById("aviso-sin-bloques");

  function opcion(valor, texto, deshabilitada) {
    var elemento = document.createElement("option");
    elemento.value = valor;
    elemento.textContent = texto;
    if (deshabilitada) {
      elemento.disabled = true;
    }
    return elemento;
  }

  function reiniciarBloque() {
    bloque.innerHTML = "";
    bloque.appendChild(opcion("", "Elige un bloque"));
  }

  if (fecha && bloque) {
    fecha.addEventListener("change", function () {
      if (!fecha.value) {
        reiniciarBloque();
        if (aviso) {
          aviso.style.display = "none";
        }
        return;
      }
      fetch("/buscar/bloques/?fecha=" + encodeURIComponent(fecha.value))
        .then(function (response) {
          return response.json();
        })
        .then(function (data) {
          var actual = bloque.value;
          reiniciarBloque();
          if (!data.bloques || !data.bloques.length) {
            bloque.appendChild(opcion("", "Sin bloques disponibles", true));
            if (aviso) {
              aviso.style.display = "";
            }
            return;
          }
          data.bloques.forEach(function (item) {
            var elemento = opcion(item.valor, item.etiqueta);
            if (item.valor === actual) {
              elemento.selected = true;
            }
            bloque.appendChild(elemento);
          });
          if (aviso) {
            aviso.style.display = "none";
          }
          /* Con la fecha nueva y un bloque aún válido, se filtra solo;
           * si el bloque se reinició, espera a que el usuario elija. */
          enviarSiCompleto(fecha.closest("form"));
        })
        .catch(function () {
          /* sin JS el formulario sigue validando en el servidor */
        });
    });
  }

  /* Filtros reactivos: envían el formulario al cambiar una opción.
   * Es una comodidad: sin JavaScript, el botón Filtrar sigue funcionando.
   * La búsqueda de texto no se envía sola para no recargar mientras se escribe. */
  document.querySelectorAll("[data-auto-submit]").forEach(function (formulario) {
    formulario
      .querySelectorAll("select, input[type=checkbox]")
      .forEach(function (campo) {
        campo.addEventListener("change", function () {
          enviarSiCompleto(formulario);
        });
      });
  });

  /* Diálogos de confirmación: devolución y cancelación */
  var pendingForm = null;
  var activeDialog = null;

  function closeDialog() {
    if (activeDialog && typeof activeDialog.close === "function") {
      activeDialog.close();
    }
    pendingForm = null;
    activeDialog = null;
  }

  document.querySelectorAll("[data-modal-form]").forEach(function (button) {
    button.addEventListener("click", function (event) {
      var dialog = document.getElementById(
        button.getAttribute("data-modal-target") || "modal-devolucion"
      );
      if (!dialog || typeof dialog.showModal !== "function") {
        return; /* sin <dialog>: el formulario se envía normalmente */
      }
      event.preventDefault();
      var form = document.getElementById(button.getAttribute("data-modal-form"));
      if (!form) {
        return;
      }
      pendingForm = form;
      activeDialog = dialog;
      var detail = dialog.querySelector("[data-modal-detail]");
      if (detail) {
        detail.textContent = button.getAttribute("data-modal-detail") || "";
      }
      dialog.showModal();
    });
  });

  document.querySelectorAll("dialog.modal").forEach(function (dialog) {
    dialog.querySelectorAll("[data-modal-close]").forEach(function (button) {
      button.addEventListener("click", closeDialog);
    });

    var confirmButton = dialog.querySelector("[data-modal-confirm]");
    if (confirmButton) {
      confirmButton.addEventListener("click", function () {
        if (!pendingForm) {
          return;
        }
        var form = pendingForm;
        closeDialog();
        if (typeof form.checkValidity === "function" && !form.checkValidity()) {
          form.reportValidity();
          return;
        }
        form.submit();
      });
    }

    dialog.addEventListener("cancel", closeDialog);
  });
})();
