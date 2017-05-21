from django import forms

from widget.models import Widget


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
            and self.widget.quantity_left is not None
            and quantity > self.widget.quantity_left
        ):
            self.add_error("quantity", "Widget is out of stock")
