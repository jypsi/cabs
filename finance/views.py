from .utils import get_provider


def start(request):
    provider = get_provider()
    return provider.handle_start(request)


def success(request):
    provider = get_provider()
    return provider.handle_success(request)


def cancel(request):
    provider = get_provider()
    return provider.handle_cancel(request)
