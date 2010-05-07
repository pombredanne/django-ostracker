import operator
from django import template

register = template.Library()

@register.simple_tag
def scaled_bar_chart(w, h, data):
    template = '''<img src="http://chart.apis.google.com/chart?cht=bhs&chs=%(w)sx%(h)s&chd=t:%(vals)s&chco=%(color)s&chxr=0,0,%(max)s,1&chds=0,%(max)s&chxt=x,y&chxl=1:|%(labels)s">'''

    variables = {
        'w': w, 'h': h,
        'color': '009900',
        'vals': ','.join(str(x) for x in data.values()),
        'labels': '|'.join(data.keys()),
        'max': max(data.values())
    }

    return template % variables

@register.simple_tag
def scaled_line_chart(w, h, data):
    template = '''<img src="http://chart.apis.google.com/chart?cht=lc&chs=%(w)sx%(h)s&chd=t:%(vals)s&chco=%(color)s&chyr=0,0,%(max)s,1&chys=0,%(max)s&chxt=y">'''

    vals = '|'.join(','.join(str(x) for x in dataset)
                    for dataset in data.values())

    max_val = max(reduce(operator.add, data.values()))
    variables = {
        'w': w, 'h': h,
        'color': '009900',
        'vals': vals,
#        'labels': '|'.join(data.keys()),
        'max': max_val,
    }

    return template % variables

@register.simple_tag
def render_proj_variable(proj_variable):
    template = '''%(last)s <img src="http://chart.apis.google.com/chart?chs=80x30&cht=ls&chco=000099&chf=bg,s,00000000&chls=1,0,0&chd=t:%(all)s&chds=0,%(max)s">'''

    variables = {
        'last': proj_variable[-1],
        'all': ','.join(str(x) for x in proj_variable),
        'max': max(proj_variable)+1
    }

    return template % variables
