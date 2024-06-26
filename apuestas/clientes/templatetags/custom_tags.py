from django import template

register = template.Library()

@register.filter(name='es_video')
def es_video(url):
    return url.lower().endswith('.mp4')
