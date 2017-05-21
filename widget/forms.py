from django import forms
from django.forms import ModelForm

from widget.models import Widget


class WidgetForm(ModelForm):
    class Meta:
        model = Widget
        fields = ["category", "price", "name", "description", "quantity", "features"]

    def clean_features(self):
        category = self.cleaned_data["category"]
        category_features = category.feature_set.all()

        for feature in self.cleaned_data["features"].all():
            if feature not in category_features:
                raise forms.ValidationError("Attempt to add invalid feature")
        return self.cleaned_data["features"]


class UpdateWidgetForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, required=False)
    price = forms.DecimalField(required=False)


class OrderWidgetForm(forms.Form):
    widget_id = forms.IntegerField(min_value=1)
    quantity = forms.IntegerField(min_value=1)

    def clean_widget_id(self):
        widget_id = self.cleaned_data["widget_id"]
        try:
            self.widget = Widget.objects.get(id=widget_id)
        except Widget.DoesNotExist:
            raise forms.ValidationError("Widget does not exist")
        return widget_id

    def clean(self):
        cleaned_data = super(OrderWidgetForm, self).clean()
        quantity = cleaned_data.get("quantity")
        if (
            quantity is not None
            # if quantity_left is None, there are infinite available
            and self.widget.quantity is not None
            and quantity > self.widget.quantity
        ):
            self.add_error("quantity", "Not enough widgets in stock")
