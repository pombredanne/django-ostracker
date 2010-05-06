from django import template

register = template.Library()

@register.simple_tag
def render_proj_variable(proj_variable):
    template = '''%(last)s
<img src="http://chart.apis.google.com/chart?chs=80x30&cht=ls&chco=000099&chf=bg,s,00000000&chls=1,0,0&chd=t:%(all)s&chds=0,%(max)s">
<span class="delta">%(delta)s</span>'''

    variables = {
        'last': proj_variable[-1],
        'all': ','.join([str(x) for x in proj_variable]),
        'max': max(proj_variable)+1,
        'delta': proj_variable[-1] - proj_variable[-2]
    }

    return template % variables

