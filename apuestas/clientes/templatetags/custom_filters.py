from django import template

register = template.Library()

@register.filter(name='is_video')
def is_video(file_url):
    return file_url.endswith('.mp4')
