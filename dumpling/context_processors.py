from .models import DumplingSize, DumplingTasty, DumplingMeat


def nav_context(request):
    return {
        'meat': DumplingMeat.objects.order_by('id').all(),
        'size': DumplingSize.objects.order_by("id").all(),
        'tasty': DumplingTasty.objects.order_by("id").all(),
    }
