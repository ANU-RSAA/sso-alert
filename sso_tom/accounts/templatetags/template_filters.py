"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from django import template

register = template.Library()


@register.filter
def field_type(field):
    """
    Returns the field type of an input
    :param field: input field
    :return: string representing the class name
    """
    return field.field.widget.__class__.__name__
