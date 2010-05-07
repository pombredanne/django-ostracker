import operator
from django import template

register = template.Library()

@register.simple_tag
def scaled_bar_chart(w, h, data):
    template = '''<img src="http://chart.apis.google.com/chart?cht=bhs&chs=%(w)sx%(h)s&chd=t:%(vals)s&chco=%(color)s&chxr=0,0,%(max)s&chds=0,%(max)s&chxt=x,y&chxl=1:|%(labels)s&chm=N,000000,0,-1,12">'''

    variables = {
        'w': w, 'h': h,
        'color': '009900',
        'vals': ','.join(str(x) for x in data.values()),
        'labels': '|'.join(reversed(data.keys())),
        'max': max(data.values())
    }

    return template % variables

@register.simple_tag
def bug_chart(w, h, data):
    template = '''<img src="http://chart.apis.google.com/chart?cht=lc&chs=%(w)sx%(h)s&chd=t:%(vals)s&chco=009900,990000&chxr=0,0,%(max)s&chds=0,%(max)s&chxt=y&chm=B,00990055,0,1,0|b,99000055,0,1,0|N,009900,0,%(n)s,12|N,990000,1,%(n)s,12">'''

    closed = data['closed']
    print data['closed'][0], data['open'][0]
    total = [x+y for x,y in zip(data['closed'], data['open'])]

    vals = ','.join(str(x) for x in closed) + '|' + ','.join(str(x) for x in total)

    max_val = max(total)
    variables = {
        'w': w, 'h': h, 'n': len(vals),
        'color': '009900,990000',
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
