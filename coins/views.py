from django.http import HttpResponse
from django.template import loader

def coins(request):
    template = loader.get_template('coins.html')
    return HttpResponse(template.render())