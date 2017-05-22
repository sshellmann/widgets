import json

from django.test import TestCase
from rest_framework.test import APIClient

from widget.models import Widget, Category, Feature, Order, OrderItem


class TestCaseWithData(TestCase):
    def setUp(self):
        self.cat1 = Category.objects.create(name="cat1", label="category1")
        self.cat2 = Category.objects.create(name="cat2", label="category2")
        self.feature1 = Feature.objects.create(label="Small", category=self.cat1)
        self.feature2 = Feature.objects.create(label="Red", category=self.cat1)
        self.feature3 = Feature.objects.create(label="Big", category=self.cat2)
        self.feature4 = Feature.objects.create(label="Blue", category=self.cat2)
        self.feature5 = Feature.objects.create(label="Fluffy", category=self.cat2)
        self.widget1 = Widget.objects.create(category=self.cat1, price="10.00", name="widget1", description="first widget")
        self.widget1.features.add(self.feature1)
        self.widget1.features.add(self.feature2)
        self.widget2 = Widget.objects.create(category=self.cat2, price="20.00", name="widget2", description="second widget")
        self.widget2.features.add(self.feature3)
        self.widget2.features.add(self.feature4)
        self.widget3 = Widget.objects.create(category=self.cat2, price="30.00", name="widget3", description="third widget")
        self.widget3.features.add(self.feature3)
        self.widget3.features.add(self.feature5)


class EmptyWidgetTestCase(TestCase):
    def test_no_widgets(self):
        client = APIClient()
        response = client.get("/widget/")

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "widgets": []
        }

    def test_invalid_request(self):
        client = APIClient()
        response = client.delete("/widget/")
        assert response.status_code == 405


class DataWidgetTestCase(TestCaseWithData):
    def test_all(self):
        client = APIClient()
        response = client.get("/widget/")

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat1", "features": ["Small", "Red"], "price": "10.00", "description": "first widget", "available_quantity": "unlimited", "name": "widget1"},
                {"category": "cat2", "features": ["Big", "Blue"], "price": "20.00", "description": "second widget", "available_quantity": "unlimited", "name": "widget2"},
                {"category": "cat2", "features": ["Big", "Fluffy"], "price": "30.00", "description": "third widget", "available_quantity": "unlimited", "name": "widget3"}
            ]
        }

    def test_by_id(self):
        client = APIClient()
        response = client.get("/widget/%s/" % self.widget1.id)

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat1", "features": ["Small", "Red"], "price": "10.00", "description": "first widget", "available_quantity": "unlimited", "name": "widget1"}
            ]
        }

    def test_by_category(self):
        client = APIClient()
        response = client.get("/widget/", {"category": str(self.cat1.id)})

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat1", "features": ["Small", "Red"], "price": "10.00", "description": "first widget", "available_quantity": "unlimited", "name": "widget1"}
            ]
        }

    def test_by_filter(self):
        client = APIClient()
        response = client.get("/widget/", {"features": ["Big", "Dog"]})

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat2", "price": "20.00", "features": ["Big", "Blue"], "name": "widget2", "description": "second widget", "available_quantity": "unlimited"},
                {"category": "cat2", "price": "30.00", "features": ["Big", "Fluffy"], "name": "widget3", "description": "third widget", "available_quantity": "unlimited"},
            ]
        }

        response = client.get("/widget/", {"features": ["Small", "Fluffy"]})

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat1", "price": "10.00", "features": ["Small", "Red"], "name": "widget1", "description": "first widget", "available_quantity": "unlimited"},
                {"category": "cat2", "price": "30.00", "features": ["Big", "Fluffy"], "name": "widget3", "description": "third widget", "available_quantity": "unlimited"},
            ]
        }

    def test_update(self):
        client = APIClient()
        response = client.patch("/widget/%s" % self.widget1.id, {"quantity": 20})
        assert response.status_code == 200
        widget = Widget.objects.get(id=self.widget1.id)
        assert widget.quantity == 20

        response = client.patch("/widget/%s" % self.widget1.id, {"price": 5.00})
        assert response.status_code == 200
        widget = Widget.objects.get(id=self.widget1.id)
        assert widget.price == 5.00

    def test_create(self):
        client = APIClient()
        post_data = {
            "price": "100.00",
            "quantity": 1,
            "name": "Rare Widget",
            "description": "Rare one of a kind widget",
            "category": str(self.cat1.id),
            "features": (str(self.feature1.id), str(self.feature2.id)),
        }
        response = client.post("/widget/", post_data)
        assert response.status_code == 200
        assert Widget.objects.count() == 4
        new_widget = list(Widget.objects.order_by("id"))[-1]
        assert new_widget.price == 100.00
        assert new_widget.quantity == 1
        assert new_widget.name == "Rare Widget"
        assert new_widget.description == "Rare one of a kind widget"
        assert new_widget.category == self.cat1
        assert set(feature.label for feature in new_widget.features.all()) == set(("Small", "Red"))

    def test_create_invalid_features(self):
        """
        Can only add features that are within the widgets category.
        This test will attempt to create a widget in category 1 and
        will add feature3 which is in category 2.
        """
        client = APIClient()
        post_data = {
            "price": "100.00",
            "quantity": 1,
            "name": "Rare Widget",
            "description": "Rare one of a kind widget",
            "category": str(self.cat1.id),
            "features": (str(self.feature1.id), str(self.feature3.id)),
        }
        response = client.post("/widget/", post_data)
        assert response.status_code == 400


class OrderTestCase(TestCaseWithData):
    def test_get(self):
        order = Order.objects.create()
        OrderItem.objects.create(widget=self.widget1, order=order, quantity=5)
        OrderItem.objects.create(widget=self.widget3, order=order, quantity=5)
        client = APIClient()
        response = client.get("/order/%s" % order.number)
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat1", "features": ["Small", "Red"], "price": "10.00", "description": "first widget", "order_quantity": 5, "available_quantity": "unlimited", "name": "widget1"},
                {"category": "cat2", "features": ["Big", "Fluffy"], "price": "30.00", "description": "third widget", "order_quantity": 5, "available_quantity": "unlimited", "name": "widget3"}
            ]
        }

    def test_create(self):
        assert Order.objects.count() == 0
        client = APIClient()
        response = client.post("/order/", {"widget_id": str(self.widget1.id), "quantity": "10"})
        assert response.status_code == 200
        assert Order.objects.count() == 1
        order = Order.objects.first()
        assert order.widgets.count() == 1
        assert order.widgets.first().id == self.widget1.id

    def test_delete(self):
        order = Order.objects.create()
        OrderItem.objects.create(widget=self.widget1, order=order, quantity=5)
        OrderItem.objects.create(widget=self.widget3, order=order, quantity=5)
        assert Order.objects.count() == 1
        client = APIClient()
        response = client.delete("/order/%s/" % order.number)
        assert response.status_code == 200
        assert Order.objects.count() == 0

    def test_quantity(self):
        assert Order.objects.count() == 0
        self.widget1.quantity = 5
        self.widget1.save()
        client = APIClient()
        response = client.post("/order/", {"widget_id": str(self.widget1.id), "quantity": "10"})
        assert response.status_code == 400
        assert response.content == '["* quantity\\n  * Not enough widgets in stock"]'
        assert Order.objects.count() == 0

    def test_complete(self):
        widget4 = Widget.objects.create(category=self.cat2, price="30.00", name="widget3", description="third widget", quantity=6)
        widget4.features.add(self.feature3)
        widget4.features.add(self.feature4)
        widget4.features.add(self.feature5)
        order = Order.objects.create()
        OrderItem.objects.create(widget=self.widget1, order=order, quantity=5)
        OrderItem.objects.create(widget=widget4, order=order, quantity=5)

        client = APIClient()
        response = client.post("/order/%s/complete/" % order.number)
        assert response.status_code == 200

        order = Order.objects.get(id=order.id)
        assert order.completed

        assert Widget.objects.get(id=self.widget1.id).quantity == None
        assert Widget.objects.get(id=widget4.id).quantity == 1

    def test_complete_failure(self):
        widget4 = Widget.objects.create(category=self.cat2, price="30.00", name="widget3", description="third widget", quantity=4)
        widget4.features.add(self.feature3)
        widget4.features.add(self.feature4)
        widget4.features.add(self.feature5)
        order = Order.objects.create()
        OrderItem.objects.create(widget=self.widget1, order=order, quantity=5)
        OrderItem.objects.create(widget=widget4, order=order, quantity=5)

        client = APIClient()
        response = client.post("/order/%s/complete/" % order.number)
        assert response.status_code == 400


class OrderItemTestCase(TestCaseWithData):
    def test_get(self):
        order = Order.objects.create()
        OrderItem.objects.create(widget=self.widget1, order=order, quantity=5)
        OrderItem.objects.create(widget=self.widget3, order=order, quantity=5)
        client = APIClient()
        response = client.get("/order/%s/item/" % order.number)
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat1", "features": ["Small", "Red"], "price": "10.00", "description": "first widget", "order_quantity": 5, "available_quantity": "unlimited", "name": "widget1"},
                {"category": "cat2", "features": ["Big", "Fluffy"], "price": "30.00", "description": "third widget", "order_quantity": 5, "available_quantity": "unlimited", "name": "widget3"}
            ]
        }

        response = client.get("/order/%s/item/%s" % (order.number, self.widget1.id))
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat1", "features": ["Small", "Red"], "price": "10.00", "description": "first widget", "order_quantity": 5, "available_quantity": "unlimited", "name": "widget1"},
                {"category": "cat2", "features": ["Big", "Fluffy"], "price": "30.00", "description": "third widget", "order_quantity": 5, "available_quantity": "unlimited", "name": "widget3"}
            ]
        }

    def test_create(self):
        order = Order.objects.create()
        OrderItem.objects.create(widget=self.widget1, order=order, quantity=5)
        client = APIClient()
        response = client.post("/order/%s/item/" % order.number, {"widget_id": str(self.widget3.id), "quantity": "10"})
        assert response.status_code == 200
        order = Order.objects.first()
        assert order.widgets.count() == 2
        widget_items = order.widgets.all()
        assert widget_items[0].id == self.widget1.id
        assert widget_items[1].id == self.widget3.id

    def test_delete(self):
        order = Order.objects.create()
        item1 = OrderItem.objects.create(widget=self.widget1, order=order, quantity=5)
        item2 = OrderItem.objects.create(widget=self.widget2, order=order, quantity=5)
        client = APIClient()

        response = client.delete("/order/%s/item/%s" % (order.number, item1.id))
        assert response.status_code == 200
        assert Order.objects.count() == 1
        order = Order.objects.first()
        assert order.widgets.count() == 1

        response = client.delete("/order/%s/item/%s" % (order.number, item2.id))
        assert response.status_code == 200
        assert Order.objects.count() == 0
