/* BibliotecaViva — mejoras de interfaz progresivas (sin frameworks).
 *
 * Ninguna acción depende de este archivo: los formularios funcionan con
 * JavaScript desactivado. Aquí solo se agregan comodidades de demostración.
 */
(function () {
  "use strict";

  var toastTimer = null;

  function showToast(message) {
    var toast = document.getElementById("toast");
    if (!toast) {
      return;
    }
    toast.textContent = message;
    toast.classList.add("is-visible");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(function () {
      toast.classList.remove("is-visible");
    }, 2600);
  }

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

  /* Cargar credenciales ficticias de demostración */
  document.querySelectorAll("[data-demo-user]").forEach(function (button) {
    button.addEventListener("click", function () {
      var username = document.getElementById("id_username");
      var password = document.getElementById("id_password");
      if (!username || !password) {
        return;
      }
      username.value = button.getAttribute("data-demo-user");
      password.value = button.getAttribute("data-demo-pass");
      showToast("Credencial de demostración cargada");
      password.focus();
    });
  });

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
