from django import template

register = template.Library()


@register.inclusion_tag("components/image_slider.html")
def image_slider(card):
    return {
        "card": card,
    }
