"""Filtros de formularios (accesibilidad y estados de error)."""
from django import template

register = template.Library()


@register.filter
def widget_con_error(bound_field, error_id):
    """Renderiza el widget marcando el campo cuando tiene errores."""
    attrs = {}
    if bound_field.errors:
        attrs = {
            "class": "campo campo--error",
            "aria-invalid": "true",
            "aria-describedby": error_id,
        }
    return bound_field.as_widget(attrs=attrs)
