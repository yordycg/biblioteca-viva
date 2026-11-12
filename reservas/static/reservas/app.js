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

  /* Actualizar los bloques disponibles al cambiar la fecha (RF-01) */
  var fecha = document.getElementById("id_fecha");
  var bloque = document.getElementById("id_bloque");
  var aviso = document.getElementById("aviso-sin-bloques");

  if (fecha && bloque) {
    fecha.addEventListener("change", function () {
      if (!fecha.value) {
        return;
      }
      fetch("/buscar/bloques/?fecha=" + encodeURIComponent(fecha.value))
        .then(function (response) {
          return response.json();
        })
        .then(function (data) {
          var actual = bloque.value;
          bloque.innerHTML = "";
          if (!data.bloques || !data.bloques.length) {
            var vacio = document.createElement("option");
            vacio.value = "";
            vacio.textContent = "Sin bloques disponibles";
            vacio.disabled = true;
            vacio.selected = true;
            bloque.appendChild(vacio);
            if (aviso) {
              aviso.style.display = "";
            }
            return;
          }
          data.bloques.forEach(function (item) {
            var option = document.createElement("option");
            option.value = item.valor;
            option.textContent = item.etiqueta;
            if (item.valor === actual) {
              option.selected = true;
            }
            bloque.appendChild(option);
          });
          if (aviso) {
            aviso.style.display = "none";
          }
        })
        .catch(function () {
          /* sin JS el formulario sigue validando en el servidor */
        });
    });
  }

  /* Diálogo de confirmación de devolución */
  var dialog = document.getElementById("modal-devolucion");
  var pendingForm = null;

  function closeDialog() {
    if (dialog && typeof dialog.close === "function") {
      dialog.close();
    }
    pendingForm = null;
  }

  document.querySelectorAll("[data-modal-form]").forEach(function (button) {
    button.addEventListener("click", function (event) {
      if (!dialog || typeof dialog.showModal !== "function") {
        return; /* sin <dialog>: el formulario se envía normalmente */
      }
      event.preventDefault();
      var form = document.getElementById(button.getAttribute("data-modal-form"));
      if (!form) {
        return;
      }
      pendingForm = form;
      var detail = dialog.querySelector("[data-modal-detail]");
      if (detail) {
        detail.textContent = button.getAttribute("data-modal-detail") || "";
      }
      dialog.showModal();
    });
  });

  if (dialog) {
    dialog.querySelectorAll("[data-modal-close]").forEach(function (button) {
      button.addEventListener("click", closeDialog);
    });

    var confirmButton = dialog.querySelector("[data-modal-confirm]");
    if (confirmButton) {
      confirmButton.addEventListener("click", function () {
        if (pendingForm) {
          var form = pendingForm;
          pendingForm = null;
          form.submit();
        }
      });
    }

    dialog.addEventListener("cancel", closeDialog);
  }
})();
