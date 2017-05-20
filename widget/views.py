from operator import and_, or_

from django.http import HttpResponse, JsonResponse
from django.db.models import Q

from widget.models import Widget, Order


def get_widget_data(widgets):
    widget_data = [
        {
            "name": widget.name,
            "description": widget.description,
            "category": widget.category.name,
            "features": [feature.label for feature in widget.features.all()],
            "price": widget.price,
        } for widget in widgets
    ]
    return widget_data


def widget_(request):
    if request.method == "GET":
        widgets = Widget.objects.all()

        category_id = request.GET.get("category")
        if category_id:
            widgets = widgets.filter(category__id = category_id)

        # getlist on a QueryDict acts like it is multiple values coming from a checkbox with the same key
        features = request.GET.getlist("features")
        if features:
            feature_filters = []
            for feature in features:
                feature_filters.append(Q(features__label__contains = feature))
            widgets = widgets.filter(reduce(or_, feature_filters))

        widgets = widgets.order_by("category__name")
        widgets = widgets.select_related("category").prefetch_related("features")
        widgets = widgets.all()

        return JsonResponse({"widgets": get_widget_data(widgets)})
    else:
        # Will need to bring in django-rest framework to properly handle this
        raise Exception("405")


def order(request):
    if request.method == "GET":
        order_number = request.GET.get("order_number")
        order = Order.objects.get(number=order_number)
        return JsonResponse({"widgets": get_widget_data(order.widgets.all())})
    else:
        widget_id = request.POST.get("widget_id")
        widget = Widget.objects.get(id=widget_id)

        order = Order.objects.create()
        order.widgets.add(widget)
        return HttpResponse(order.number)

def order_item(request):
    pass
