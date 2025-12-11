from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    """
    Сохраняет текущие параметры GET-запроса и добавляет новые.
    Пример: {% querystring page=coins.next_page_number %}
    """
    request = context.get('request')
    if not request:
        return ''
    params = request.GET.copy()
    for key, value in kwargs.items():
        params[key] = value
    return params.urlencode()