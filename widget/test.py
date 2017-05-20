import json

from django.test import TestCase, Client
from django.utils.datastructures import MultiValueDict

from widget.models import Widget, Category, Feature, Order


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
    def test_empty(self):
        client = Client()
        response = client.get("/widget/")

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "widgets": []
        }


class WidgetTestCaseWithData(TestCaseWithData):
    def test_all(self):
        client = Client()
        response = client.get("/widget/")

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat1", "price": "10.00", "features": ["Small", "Red"], "name": "widget1", "description": "first widget"},
                {"category": "cat2", "price": "20.00", "features": ["Big", "Blue"], "name": "widget2", "description": "second widget"},
                {"category": "cat2", "price": "30.00", "features": ["Big", "Fluffy"], "name": "widget3", "description": "third widget"}
            ]
        }

    def test_by_category(self):
        client = Client()
        response = client.get("/widget/", {"category": self.cat1.id})

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat1", "price": "10.00", "features": ["Small", "Red"], "name": "widget1", "description": "first widget"}
            ]
        }

    def test_by_filter(self):
        client = Client()
        response = client.get("/widget/", {"features": ["Big", "Dog"]})

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat2", "price": "20.00", "features": ["Big", "Blue"], "name": "widget2", "description": "second widget"},
                {"category": "cat2", "price": "30.00", "features": ["Big", "Fluffy"], "name": "widget3", "description": "third widget"}
            ]
        }

        response = client.get("/widget/", {"features": ["Small", "Fluffy"]})

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat1", "price": "10.00", "features": ["Small", "Red"], "name": "widget1", "description": "first widget"},
                {"category": "cat2", "price": "30.00", "features": ["Big", "Fluffy"], "name": "widget3", "description": "third widget"}
            ]
        }


class OrderTestCase(TestCaseWithData):
    def test_get(self):
        new_order = Order.objects.create()
        new_order.widgets.add(self.widget1)
        new_order.widgets.add(self.widget3)
        client = Client()
        response = client.get("/order/", {"order_number": new_order.number})
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat1", "price": "10.00", "features": ["Small", "Red"], "name": "widget1", "description": "first widget"},
                {"category": "cat2", "price": "30.00", "features": ["Big", "Fluffy"], "name": "widget3", "description": "third widget"}
            ]
        }


    def test_create(self):
        assert Order.objects.count() == 0
        client = Client()
        response = client.post("/order/", {"widget_id": self.widget1.id})
        assert response.status_code == 200
        assert Order.objects.count() == 1
        order = Order.objects.first()
        assert order.widgets.count() == 1
        assert order.widgets.first().id == self.widget1.id
