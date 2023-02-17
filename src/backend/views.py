from django.http import HttpResponse
from django.http import JsonResponse
from .models import Software


def index(request):
    return HttpResponse("Hello, world.")


def get_software_list(request):
    software_items = Software.objects.all()
    data = {"payload": list(software_items.values())}
    return JsonResponse(data)


def get_software_details(request, software_id):
    software = Software.objects.filter(id=software_id).first()
    if software is None:
        data = {"payload": None}
    else:
        data = {"payload": {
            "id": software.id,
            "fullname": software.fullname,
            "editor": software.editor
        }}
    return JsonResponse(data)
