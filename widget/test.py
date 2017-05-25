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
        assert json.loads(response.content) == []

    def test_invalid_request(self):
        client = APIClient()
        response = client.delete("/widget/")
        assert response.status_code == 405


class DataWidgetTestCase(TestCaseWithData):
    def test_all(self):
        client = APIClient()
        response = client.get("/widget/")

        assert response.status_code == 200
        widgets = json.loads(response.content)
        assert len(widgets) == 3
        assert widgets[0]["category"] == "cat1"
        assert widgets[0]["features"] == ["Small", "Red"]
        assert widgets[0]["price"] == "10.00"
        assert widgets[0]["name"] == "widget1"
        assert widgets[0]["description"] == "first widget"
        assert widgets[0]["quantity"] == None

        assert widgets[1]["category"] == "cat2"
        assert widgets[1]["features"] == ["Big", "Blue"]
        assert widgets[1]["price"] == "20.00"
        assert widgets[1]["name"] == "widget2"
        assert widgets[1]["description"] == "second widget"
        assert widgets[1]["quantity"] == None

        assert widgets[2]["category"] == "cat2"
        assert widgets[2]["features"] == ["Big", "Fluffy"]
        assert widgets[2]["price"] == "30.00"
        assert widgets[2]["name"] == "widget3"
        assert widgets[2]["description"] == "third widget"
        assert widgets[2]["quantity"] == None

    def test_by_id(self):
        client = APIClient()
        response = client.get("/widget/%s/" % self.widget1.id)

        assert response.status_code == 200

        widget = json.loads(response.content)
        assert widget["category"] == "cat1"
        assert widget["features"] == ["Small", "Red"]
        assert widget["price"] == "10.00"
        assert widget["name"] == "widget1"
        assert widget["description"] == "first widget"
        assert widget["quantity"] == None

    def test_by_category(self):
        client = APIClient()
        response = client.get("/widget/", {"category": str(self.cat1.id)})

        assert response.status_code == 200

        widgets = json.loads(response.content)
        assert len(widgets) == 1
        assert widgets[0]["category"] == "cat1"
        assert widgets[0]["features"] == ["Small", "Red"]
        assert widgets[0]["price"] == "10.00"
        assert widgets[0]["name"] == "widget1"
        assert widgets[0]["description"] == "first widget"
        assert widgets[0]["quantity"] == None

    def test_by_filter(self):
        client = APIClient()
        response = client.get("/widget/", {"features": ["Big", "Dog"]})

        assert response.status_code == 200

        widgets = json.loads(response.content)
        assert len(widgets) == 2
        assert widgets[0]["category"] == "cat2"
        assert widgets[0]["features"] == ["Big", "Blue"]
        assert widgets[0]["price"] == "20.00"
        assert widgets[0]["name"] == "widget2"
        assert widgets[0]["description"] == "second widget"
        assert widgets[0]["quantity"] == None

        assert widgets[1]["category"] == "cat2"
        assert widgets[1]["features"] == ["Big", "Fluffy"]
        assert widgets[1]["price"] == "30.00"
        assert widgets[1]["name"] == "widget3"
        assert widgets[1]["description"] == "third widget"
        assert widgets[1]["quantity"] == None

        response = client.get("/widget/", {"features": ["Small", "Fluffy"]})

        assert response.status_code == 200

        widgets = json.loads(response.content)
        assert len(widgets) == 2
        assert widgets[0]["category"] == "cat1"
        assert widgets[0]["features"] == ["Small", "Red"]
        assert widgets[0]["price"] == "10.00"
        assert widgets[0]["name"] == "widget1"
        assert widgets[0]["description"] == "first widget"
        assert widgets[0]["quantity"] == None

        assert widgets[1]["category"] == "cat2"
        assert widgets[1]["features"] == ["Big", "Fluffy"]
        assert widgets[1]["price"] == "30.00"
        assert widgets[1]["name"] == "widget3"
        assert widgets[1]["description"] == "third widget"
        assert widgets[1]["quantity"] == None

    def test_update(self):
        assert Widget.objects.count() == 3
        client = APIClient()
        put_data = {
            "price": "5.00",
            "quantity": "20",
            "name": "Common Widget",
            "description": "Not very popular widget",
            "category": str(self.widget2.category.id),
            "features": (str(self.feature3.id), str(self.feature4.id)),
        }
        response = client.put("/widget/%s" % self.widget2.id, put_data)
        assert response.status_code == 200
        assert Widget.objects.count() == 3
        widget = Widget.objects.get(id=self.widget2.id)
        assert widget.name == "Common Widget"
        assert widget.description == "Not very popular widget"
        assert widget.quantity == 20
        assert widget.price == 5.00
        assert [feature.id for feature in widget.features.all()] == [self.feature3.id, self.feature4.id]

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
        assert response.status_code == 201
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
        assert response.content == '{"non_field_errors":["Features must all apply to chosen category."]}'


class OrderTestCase(TestCaseWithData):
    def test_get(self):
        order = Order.objects.create()
        item1 = OrderItem.objects.create(widget=self.widget1, order=order, quantity=5)
        item2 = OrderItem.objects.create(widget=self.widget3, order=order, quantity=5)
        client = APIClient()
        response = client.get("/order/%s" % order.number)
        assert response.status_code == 200

        assert json.loads(response.content) == {
            "items": [
                {
                    "id": item1.id,
                    "widget": {
                        "category": "cat1",
                        "description": "first widget",
                        "price": "10.00",
                        "features": [
                            "Small",
                            "Red"
                        ],
                        "quantity": None,
                        "id": self.widget1.id,
                        "name": "widget1"
                    },
                    "order": 1,
                    "quantity": 5
                },
                {
                    "id": item2.id,
                    "widget": {
                        "category": "cat2",
                        "description": "third widget",
                        "price": "30.00",
                        "features": [
                            "Big",
                            "Fluffy"
                        ],
                        "quantity": None,
                        "id": self.widget3.id,
                        "name": "widget3"
                    },
                    "order": 1,
                    "quantity": 5
                }
            ],
            "completed": False,
            "id": order.id,
            "number": order.number
        }

    def test_get_completed(self):
        order = Order.objects.create(completed=True)
        OrderItem.objects.create(widget=self.widget1, order=order, quantity=5)
        client = APIClient()
        response = client.get("/order/%s" % order.number)
        assert response.status_code == 400


    def test_create(self):
        assert Order.objects.count() == 0
        client = APIClient()
        response = client.post("/order/", {"widget": str(self.widget1.id), "quantity": "10"})
        assert response.status_code == 201
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
        response = client.post("/order/", {"widget": str(self.widget1.id), "quantity": "10"})
        assert response.status_code == 400
        assert response.content == '{"non_field_errors":["Not enough supply to satisfy order."]}'
        assert Order.objects.count() == 0

    def test_complete(self):
        widget4 = Widget.objects.create(category=self.cat2, price="30.00", name="widget4", description="fourth widget", quantity=6)
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
        widget4 = Widget.objects.create(category=self.cat2, price="30.00", name="widget4", description="fourth widget", quantity=4)
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
        order_item = OrderItem.objects.create(widget=self.widget1, order=order, quantity=5)
        OrderItem.objects.create(widget=self.widget3, order=order, quantity=5)
        client = APIClient()
        response = client.get("/order/item/")
        assert response.status_code == 403

        response = client.get("/order/item/%s" % order_item.id)
        assert response.status_code == 200

        assert json.loads(response.content) == {
            "id": order_item.id,
            "widget": {
                "category": "cat1",
                "description": "first widget",
                "price": "10.00",
                "features": [
                    "Small",
                    "Red"
                ],
                "quantity": None,
                "id": self.widget1.id,
                "name": "widget1"
            },
            "order": order.id,
            "quantity": 5
        }

    def test_create(self):
        order = Order.objects.create()
        OrderItem.objects.create(widget=self.widget1, order=order, quantity=5)
        client = APIClient()
        response = client.post("/order/item/", {"order": str(order.id), "widget": str(self.widget3.id), "quantity": "10"})
        assert response.status_code == 201
        order = Order.objects.first()
        assert order.widgets.count() == 2
        widget_items = order.widgets.all()
        assert widget_items[0].id == self.widget1.id
        assert widget_items[1].id == self.widget3.id

    def test_update(self):
        order = Order.objects.create()
        order_item = OrderItem.objects.create(widget=self.widget1, order=order, quantity=5)
        client = APIClient()
        response = client.put("/order/item/%s" % order_item.id, {"order": str(order_item.order.id), "widget": str(order_item.widget.id), "quantity": "10"})
        assert response.status_code == 200
        order = Order.objects.first()
        assert order.widgets.count() == 1
        assert OrderItem.objects.first().quantity == 10

    def test_delete(self):
        order = Order.objects.create()
        item1 = OrderItem.objects.create(widget=self.widget1, order=order, quantity=5)
        item2 = OrderItem.objects.create(widget=self.widget2, order=order, quantity=5)
        client = APIClient()

        response = client.delete("/order/item/%s" % item1.id)
        assert response.status_code == 200
        assert Order.objects.count() == 1
        order = Order.objects.first()
        assert order.widgets.count() == 1

        response = client.delete("/order/item/%s" % item2.id)
        assert response.status_code == 200
        assert Order.objects.count() == 0
