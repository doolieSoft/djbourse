from django.template.defaultfilters import register


@register.filter
def dict_key(h, key):
    return h[key]