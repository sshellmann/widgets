from rest_framework import serializers, fields

from widget.models import Widget, Category, Feature, Order, OrderItem


class CategoryRepresentation(serializers.RelatedField):
    def to_representation(self, obj):
        return obj.name

    def to_internal_value(self, data):
        try:
            try:
                return Category.objects.get(id=int(data))
            except KeyError:
                raise serializers.ValidationError('Category is a required field.')
            except ValueError:
                raise serializers.ValidationError('Category must be an integer.')
        except Category.DoesNotExist:
            raise serializers.ValidationError('Category does not exist.')


class FeaturesRepresentation(serializers.RelatedField):
    def to_representation(self, obj):
        return obj.label

    def to_internal_value(self, data):
        try:
            try:
                return Feature.objects.get(id=int(data))
            except KeyError:
                raise serializers.ValidationError('Feature is a required field.')
            except ValueError:
                raise serializers.ValidationError('Feature must be an integer.')
        except Feature.DoesNotExist:
            raise serializers.ValidationError('Feature does not exist.')


class WidgetsRepresentation(serializers.RelatedField):
    def to_representation(self, obj):
        return obj.name

    def to_internal_value(self, data):
        try:
            try:
                return Widget.objects.get(id=int(data))
            except KeyError:
                raise serializers.ValidationError('Widget is a required field.')
            except ValueError:
                raise serializers.ValidationError('Widget must be an integer.')
        except Widget.DoesNotExist:
            raise serializers.ValidationError('Widget does not exist.')


def validate_features(data):
    for submitted_feature in data["features"]:
        if submitted_feature.category != data["category"]:
            raise serializers.ValidationError("Features must all apply to chosen category.")


class WidgetSerializer(serializers.ModelSerializer):
    category = CategoryRepresentation(queryset=Category.objects.all())
    features = FeaturesRepresentation(many=True, queryset=Feature.objects.all())

    class Meta:
        model = Widget
        fields = ("id", "category", "price", "features", "name", "description", "quantity")
        validators = [validate_features]


class OrderRepresentation(serializers.RelatedField):
    def to_representation(self, obj):
        return obj.id

    def to_internal_value(self, data):
        try:
            try:
                return Order.objects.get(id=int(data))
            except KeyError:
                raise serializers.ValidationError('Order is a required field.')
            except ValueError:
                raise serializers.ValidationError('Order must be an integer.')
        except Order.DoesNotExist:
            raise serializers.ValidationError('Order does not exist.')


def validate_quantity(data):
    if data["widget"].quantity is not None and data["widget"].quantity < data["quantity"]:
        raise serializers.ValidationError("Not enough supply to satisfy order.")


class OrderItemWidgetRepresentation(WidgetSerializer):
    """
    Nested serializers are a mess. https://stackoverflow.com/a/28016439/2689986
    This lets us accept ids when saving / updating instead of nested objects.
    Representation would be into an object (depending on model_serializer).
    """
    # Override validators set by the widget serializer which are not necessary
    validators = []
    # Force this serializer to act like a field while writing
    def get_value(*args, **kwargs):
        return fields.Field.get_value(*args, **kwargs)

    def to_internal_value(self, data):
        try:
            return Widget.objects.get(pk=data)
        except Widget.DoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)

    def to_representation(self, data):
        return WidgetSerializer.to_representation(self, data)


class OrderItemSerializer(serializers.ModelSerializer):
    widget = OrderItemWidgetRepresentation()
    order = OrderRepresentation(queryset=Order.objects.all())

    class Meta:
        model = OrderItem
        fields = ("id", "quantity", "widget", "order")
        validators = [validate_quantity]

    def create(self, validated_data):
        order_item = OrderItem.objects.create(
            order=validated_data["order"],
            widget=validated_data["widget"],
            quantity=validated_data["quantity"]
        )
        return order_item


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Order
        fields = ("id", "number", "items", "completed")

    def create(self, validated_data):
        order = Order.objects.create()
        return order
