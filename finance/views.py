from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .utils import get_provider


def index(request):
    order_id = request.GET.get('order_id')
    return render(request, 'finance/index.html', context={'order_id': order_id})

@csrf_exempt
def start(request):
    provider = get_provider()
    return provider.handle_start(request)


@csrf_exempt
def success(request):
    provider = get_provider()
    return provider.handle_success(request)


@csrf_exempt
def cancel(request):
    provider = get_provider()
    return provider.handle_cancel(request)
