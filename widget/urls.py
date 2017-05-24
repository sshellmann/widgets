"""widget URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from widget.views import ui, widget_, order_, order_item, order_complete

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url('^$', ui),
    url(r'^widget/(?P<widget_id>[0-9]+)?/?$', widget_),
    url(r'^order/(?P<order_number>[a-f0-9]{10})?/?$', order_),
    url(r'^order/(?P<order_number>[a-f0-9]{10})/complete/$', order_complete),
    url(r'^order/item/(?P<order_item_id>[0-9]+)?/?$', order_item),
]
