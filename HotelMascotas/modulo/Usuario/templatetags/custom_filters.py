from django import template

register = template.Library()

@register.filter
def to(value, arg):
    return range(value, arg)


@register.filter
def get_item(dictionary, key):
    """
    Devuelve el valor asociado a una clave de un diccionario.
    Si no existe, retorna None.
    """
    value = dictionary.get(key, None)
    # Si el valor es una lista o estructura, devuelve solo el número que se espera
    if isinstance(value, list) or isinstance(value, dict):
        return len(value)  # O ajusta según la lógica necesaria
    return value