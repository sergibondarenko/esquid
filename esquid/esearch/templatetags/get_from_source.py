from django import template

register = template.Library()

@register.filter(name = 'get_from_source')
def get_from_dict(d, k):
    d = d.get('_source', None)
    return d.get(k, None)








