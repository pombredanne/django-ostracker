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
    template = '''<img src="http://chart.apis.google.com/chart?cht=bvs&chs=%(w)sx%(h)s&chd=t:%(vals)s&chco=009900,990000&chxr=0,0,%(max)s&chds=0,%(max)s&chxt=y&chm=N,000000,0,-1,12|N,000000,1,-1,12&chbh=a,5,0&chdlp=b&chdl=open|closed">'''

    vals = ','.join(str(x) for x in data['closed']) + '|' + ','.join(str(x) for x in data['open'])

    total = [x+y for x,y in zip(data['closed'], data['open'])]
    max_val = max(total)

    variables = {
        'w': w, 'h': h,
        'vals': vals,
        'max': max_val,
    }

    return template % variables

@register.simple_tag
def line_chart(w, h, data):
    template = '''<img src="http://chart.apis.google.com/chart?cht=lc&chs=%(w)sx%(h)s&chd=t:%(vals)s&chco=5500cc,cc5500,00cc55&chxr=0,0,%(max)s&chds=0,%(max)s&chxt=y&chbh=a,5,0&chdlp=b&chdl=%(labels)s&chm=N,000000,0,%(n)s,12|N,000000,1,%(n)s,12|N,000000,2,%(n)s,12">'''

    vals = '|'.join(','.join(str(x) for x in dataset) for dataset in data.values())

    total = reduce(operator.add, data.values())
    max_val = max(total)

    variables = {
        'w': w, 'h': h, 'n': len(data.values()[0]),
        'vals': vals,
        'max': max_val,
        'labels': '|'.join(data.keys()),
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
