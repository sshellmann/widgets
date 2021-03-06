# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-25 04:40
from __future__ import unicode_literals

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import widget.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('label', models.CharField(max_length=100)),
            ],
            bases=(widget.models.FullDisplayModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=100)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='widget.Category')),
            ],
            bases=(widget.models.FullDisplayModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(default=widget.models.generate_order_number, max_length=10, unique=True)),
                ('completed', models.BooleanField(default=False)),
            ],
            bases=(widget.models.FullDisplayModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='widget.Order')),
            ],
            bases=(widget.models.FullDisplayModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Widget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(max_length=1000)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='widget.Category')),
                ('features', models.ManyToManyField(to='widget.Feature', verbose_name=b'Features for this widget')),
            ],
            bases=(widget.models.FullDisplayModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='widget',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='widget.Widget'),
        ),
        migrations.AddField(
            model_name='order',
            name='widgets',
            field=models.ManyToManyField(through='widget.OrderItem', to='widget.Widget', verbose_name=b'Items in order'),
        ),
    ]
