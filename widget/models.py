import uuid
from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator
from django.contrib import admin


class FullDisplayModelMixin(object):
    def stringify_field(self, field):
        return "%s: %s" % (field.name, getattr(self, field.name))

    def __unicode__(self):
        fields = ", ".join(self.stringify_field(field) for field in self._meta.fields)
        return "<{klass}: {fields}>".format(
            klass=self.__class__.__name__,
            fields=fields
        )


class Category(FullDisplayModelMixin, models.Model):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100)


class Feature(FullDisplayModelMixin, models.Model):
    label = models.CharField(max_length=100)
    category = models.ForeignKey(Category)


class Widget(FullDisplayModelMixin, models.Model):
    category = models.ForeignKey(Category)
    price = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal('0.01'))])
    features = models.ManyToManyField(Feature, verbose_name="Features for this widget")
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)


class Order(FullDisplayModelMixin, models.Model):
    number = models.CharField(max_length=10, default=uuid.uuid4().hex[:10])
    widgets = models.ManyToManyField(Widget, verbose_name="Items in order")


class FeatureInline(admin.TabularInline):
    model = Feature

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "label")
    inlines = [FeatureInline]

def category_name(feature):
    return feature.category.name
category_name.short_description = "Category"
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("label", category_name)

class WidgetAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "description", "price")
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number",)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Widget, WidgetAdmin)
admin.site.register(Feature, FeatureAdmin)
admin.site.register(Order, OrderAdmin)
