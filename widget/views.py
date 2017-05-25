from operator import or_

from django.db.models import Q
from django.db import transaction
from django.shortcuts import render
from rest_framework import exceptions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from widget.models import Widget, Order, OrderItem, Category
from widget.serializers import WidgetSerializer, OrderSerializer, OrderItemSerializer


@api_view(["GET", "POST", "PUT"])
def widget_(request, widget_id=None):
    if request.method == "GET":
        if widget_id:
            widget = Widget.objects.get(id=int(widget_id))
            return Response(WidgetSerializer(widget).data)

        widgets = Widget.objects.all()

        category_id = request.GET.get("category")
        if category_id and category_id.isdigit():
            widgets = widgets.filter(category__id=category_id)

        # getlist on a QueryDict acts like it is multiple values coming from a checkbox with the same key
        features = request.GET.getlist("features")
        if features:
            feature_filters = []
            for feature in features:
                feature_filters.append(Q(features__label__contains=feature))
            widgets = widgets.filter(reduce(or_, feature_filters))

        widgets = widgets.order_by("category__name")
        widgets = widgets.select_related("category").prefetch_related("features")
        widgets = widgets.all()

        return Response(WidgetSerializer(widgets, many=True).data)
    elif request.method == "POST":
        serializer = WidgetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "PUT":
        if not widget_id:
            raise exceptions.ValidationError("Widget id necessary")
        widget = Widget.objects.get(id=int(widget_id))

        serializer = WidgetSerializer(widget, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST", "PUT", "DELETE"])
@transaction.atomic
def order_(request, order_number=None):
    if request.method == "GET":
        if not order_number:
            raise exceptions.PermissionDenied()
        order = Order.objects.get(number=order_number)
        return Response(OrderSerializer(order).data)
    elif request.method == "POST":
        order_serializer = OrderSerializer(data=request.data)

        if order_serializer.is_valid():
            with transaction.atomic():
                order_serializer.save()
                order_id = order_serializer.data["id"]
                data_with_order_id = dict(request.data.items() + [("order", str(order_id))])
                order_item_serializer = OrderItemSerializer(data=data_with_order_id)
                if order_item_serializer.is_valid():
                    order_item_serializer.save()
                else:
                    raise exceptions.ValidationError(order_item_serializer.errors)
            data = dict(order_serializer.data.items())
            data["items"] = [dict(order_item_serializer.data.items())]
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        order = Order.objects.get(number=order_number)
        order.delete()
        return Response()


@api_view(["POST"])
@transaction.atomic
def order_complete(request, order_number):
    order = Order.objects.get(number=order_number)
    order_items = OrderItem.objects.filter(order=order).select_related().all()
    for order_item in order_items:
        # If ordered widget quantity is unlimited, there is no need to reduce it
        if order_item.widget.quantity is not None:
            # Only remove quantity if the widget can satisfy the order
            if order_item.widget.quantity > order_item.quantity:
                order_item.widget.quantity -= order_item.quantity
                order_item.widget.save()
            else:
                raise exceptions.ValidationError("Not enough stock to fulfill order")
    order.completed = True
    order.save()
    return Response()


@api_view(["GET", "POST", "PUT", "DELETE"])
def order_item(request, order_item_id):
    if request.method == "GET":
        if not order_item_id:
            raise exceptions.NotAuthenticated
        order_item = OrderItem.objects.get(id=order_item_id)
        return Response(OrderItemSerializer(order_item).data)
    elif request.method == "POST":
        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "PUT":
        if not order_item_id:
            raise exceptions.ValidationError("Order item id necessary")
        order_item = OrderItem.objects.get(id=order_item_id)
        serializer = OrderItemSerializer(order_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        if not order_item_id:
            raise exceptions.ValidationError("Order item id necessary")
        order_item = OrderItem.objects.get(id=order_item_id)
        order = order_item.order
        order_item.delete()
        if order.orderitem_set.count() == 0:
            order.delete()
        return Response()


def ui(request):
    categories = Category.objects.all()
    return render(request, "widget/index.html", {"categories": categories})
