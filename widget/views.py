from operator import and_, or_

from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from rest_framework import exceptions

from widget.models import Widget, Order
from widget.forms import OrderWidgetForm


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


def widget_(request, widget_id=None):
    if request.method == "GET":
        if widget_id:
            widget = Widget.objects.get(id=widget_id)
            return JsonResponse({"widgets": get_widget_data([widget])})

        widgets = Widget.objects.all()

        category_id = request.GET.get("category")
        if category_id and category_id.isdigit():
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
        raise exceptions.MethodNotAllowed(request.method)


def order_(request, order_number=None):
    if request.method == "GET":
        if not order_number:
            raise exceptions.PermissionDenied()
        order = Order.objects.get(number=order_number)
        return JsonResponse({"widgets": get_widget_data(order.widgets.all())})
    elif request.method == "POST":
        form = OrderWidgetForm(request.POST)
        if form.is_valid():
            order = Order.objects.create()
            order.widgets.add(form.widget)
            return HttpResponse(order.number)
        else:
            raise exceptions.ParseError()
    elif request.method == "DELETE":
        order = Order.objects.get(number=order_number)
        order.delete()
        return HttpResponse()
    else:
        raise exceptions.MethodNotAllowed(request.method)

def order_item(request, order_number, widget_id=None):
    order = Order.objects.get(number=order_number)
    if request.method == "GET":
        if not widget_id:
            return order_(request, order_number)
        widget = Widget.objects.get(id=widget_id)
        return JsonResponse({"widgets": get_widget_data([widget])})
    elif request.method == "POST":
        form = OrderWidgetForm(request.POST)
        if form.is_valid():
            order.widgets.add(form.widget)
        else:
             raise exceptions.ParseError()
        return HttpResponse()
    else:
        raise exceptions.MethodNotAllowed(request.method)
