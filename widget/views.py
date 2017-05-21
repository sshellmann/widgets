from operator import and_, or_

from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from rest_framework import exceptions
from rest_framework.decorators import api_view

from widget.models import Widget, Order, OrderItem
from widget.forms import WidgetForm, OrderWidgetForm, UpdateWidgetForm


def get_widget_data(widgets):
    widget_data = [
        {
            "name": widget.name,
            "description": widget.description,
            "category": widget.category.name,
            "features": [feature.label for feature in widget.features.all()],
            "price": widget.price,
            "available_quantity": widget.quantity or "unlimited"
        } for widget in widgets
    ]
    return widget_data


def get_order_data(order):
    order_items = order.orderitem_set.all()
    data = []
    for order_item in order_items:
        widget_data = get_widget_data([order_item.widget])[0]
        widget_data["order_quantity"] = order_item.quantity
        data.append(widget_data)
    return data


@api_view(["GET", "POST", "PATCH"])
def widget_(request, widget_id=None):
    if request.method == "GET":
        if widget_id:
            widget = Widget.objects.get(id=int(widget_id))
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
    elif request.method == "POST":
        form = WidgetForm(request.data)
        if form.is_valid():
            form.save()
            return HttpResponse()
        else:
            raise exceptions.ValidationError(form.errors.as_text())
    elif request.method == "PATCH":
        if not widget_id:
            raise exceptions.ValidationError("Widget id necessary")
        widget = Widget.objects.get(id=int(widget_id))
        form = UpdateWidgetForm(request.data)
        if form.is_valid():
            quantity = form.cleaned_data["quantity"]
            if quantity:
                widget.quantity = quantity
            price = form.cleaned_data["price"]
            if price:
                widget.price = price
            widget.save()
        else:
            raise exceptions.ValidationError(form.errors.as_text())
        return HttpResponse()


@api_view(["GET", "POST", "DELETE"])
def order_(request, order_number=None):
    if request.method == "GET":
        if not order_number:
            raise exceptions.PermissionDenied()
        order = Order.objects.get(number=order_number)
        return JsonResponse({"widgets": get_order_data(order)})
    elif request.method == "POST":
        form = OrderWidgetForm(request.data)
        if form.is_valid():
            order = Order.objects.create()
            quantity = form.cleaned_data["quantity"]
            OrderItem.objects.create(widget=form.widget, order=order, quantity=quantity)
            return HttpResponse(order.number)
        else:
            raise exceptions.ValidationError(form.errors.as_text())
    elif request.method == "DELETE":
        order = Order.objects.get(number=order_number)
        order.delete()
        return HttpResponse()


@api_view(["GET", "POST", "DELETE"])
def order_item(request, order_number, widget_id=None):
    order = Order.objects.get(number=order_number)
    if request.method == "GET":
        if not widget_id:
            return order_(request, order_number)
        widget = Widget.objects.get(id=widget_id)
        return JsonResponse({"widgets": get_order_data(order)})
    elif request.method == "POST":
        form = OrderWidgetForm(request.data)
        if form.is_valid():
            quantity = form.cleaned_data["quantity"]
            OrderItem.objects.create(widget=form.widget, order=order, quantity=quantity)
        else:
            raise exceptions.ValidationError(form.errors.as_text())
        return HttpResponse()
    elif request.method == "DELETE":
        if not widget_id:
            raise exceptions.ValidationError("Widget id necessary")
        widget = Widget.objects.get(id=int(widget_id))
        order_item = OrderItem.objects.filter(widget=widget, order=order)
        order_item.delete()
        if order.orderitem_set.count() == 0:
            order.delete()
        return HttpResponse()
