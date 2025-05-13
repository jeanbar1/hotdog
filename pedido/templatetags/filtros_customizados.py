from django import template
import textwrap

register = template.Library()

@register.filter
def wrap_line(value, width=30):
    """Quebra o texto em várias linhas com no máximo `width` caracteres."""
    if not value:
        return ''
    return '\n'.join(textwrap.wrap(str(value), width))
