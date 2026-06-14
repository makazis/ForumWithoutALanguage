from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()
chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    
def encode_symbol(index):
    first = chars[index // 62]
    second = chars[index % 62]
    return f"{first}{second}"

def decode_symbol(code):
    return chars.index(code[0]) * 62 + chars.index(code[1])
def split_sequence(sequence):
    if not sequence: 
        return []
    return [sequence[i*2]+sequence[i*2+1] for i in range(int(len(sequence)/2))]

@register.filter
@stringfilter
def render_symbol_sequence(value):
    if not value:
        return ''
    codes = split_sequence(value)
    images = []
    for code in codes:
        if code.strip():
            images.append(f'<img src="/static/symbols/symbol_{code}.png" class="symbol-img w-8 h-8 inline-block" alt="symbol_{code}">')
    return ''.join(images)

@register.simple_tag
def symbol_img(code):
    return f'<img src="/static/symbols/symbol_{code}.png" class="symbol-img w-8 h-8 inline-block" alt="symbol_{code}">'

@register.filter
def split_sequence(value):
    return split_sequence(value)