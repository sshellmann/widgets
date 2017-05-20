import json

from django.test import TestCase, Client
from django.utils.datastructures import MultiValueDict

from widget.models import Widget, Category, Feature


class EmptyWidgetTestCase(TestCase):
    def test_empty(self):
        client = Client()
        response = client.get("/widgets/")

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "widgets": []
        }


class WidgetTestCaseWithData(TestCase):
    def setUp(self):
        self.cat1 = Category.objects.create(name="cat1", label="category1")
        self.cat2 = Category.objects.create(name="cat2", label="category2")
        feature1 = Feature.objects.create(label="Small", category=self.cat1)
        feature2 = Feature.objects.create(label="Red", category=self.cat1)
        feature3 = Feature.objects.create(label="Big", category=self.cat2)
        feature4 = Feature.objects.create(label="Blue", category=self.cat2)
        feature5 = Feature.objects.create(label="Fluffy", category=self.cat2)
        widget1 = Widget.objects.create(category=self.cat1, price="10.00", name="widget1", description="first widget")
        widget1.features.add(feature1)
        widget1.features.add(feature2)
        widget2 = Widget.objects.create(category=self.cat2, price="20.00", name="widget2", description="second widget")
        widget2.features.add(feature3)
        widget2.features.add(feature4)
        widget3 = Widget.objects.create(category=self.cat2, price="30.00", name="widget3", description="third widget")
        widget3.features.add(feature3)
        widget3.features.add(feature5)

    def test_all(self):
        client = Client()
        response = client.get("/widgets/")

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
        response = client.get("/widgets/", {"category": self.cat1.id})

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat1", "price": "10.00", "features": ["Small", "Red"], "name": "widget1", "description": "first widget"}
            ]
        }

    def test_by_filter(self):
        client = Client()
        response = client.get("/widgets/", {"features": ["Big", "Dog"]})

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat2", "price": "20.00", "features": ["Big", "Blue"], "name": "widget2", "description": "second widget"},
                {"category": "cat2", "price": "30.00", "features": ["Big", "Fluffy"], "name": "widget3", "description": "third widget"}
            ]
        }

        response = client.get("/widgets/", {"features": ["Small", "Fluffy"]})

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "widgets": [
                {"category": "cat1", "price": "10.00", "features": ["Small", "Red"], "name": "widget1", "description": "first widget"},
                {"category": "cat2", "price": "30.00", "features": ["Big", "Fluffy"], "name": "widget3", "description": "third widget"}
            ]
        }
