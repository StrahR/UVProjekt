# Generated by Django 2.2.4 on 2019-08-17 10:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connect_four', '0003_bnsai'),
    ]

    operations = [
        migrations.DeleteModel(
            name='NegamaxPrunningTTTAI',
        ),
        migrations.DeleteModel(
            name='NegimaxABTablesAI',
        ),
        migrations.CreateModel(
            name='NegamaxABTablesAI',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('connect_four.baseai',),
        ),
        migrations.CreateModel(
            name='NegamaxPruningTTTAI',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('connect_four.baseai',),
        ),
    ]
