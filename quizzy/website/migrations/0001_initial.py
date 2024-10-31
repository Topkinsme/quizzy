# Generated by Django 5.1.1 on 2024-10-31 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('q_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('question', models.CharField(max_length=200)),
                ('option_a', models.CharField(max_length=100)),
                ('option_b', models.CharField(max_length=100)),
                ('option_c', models.CharField(max_length=100)),
                ('option_d', models.CharField(max_length=100)),
                ('ans', models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('quiz_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
            ],
        ),
    ]
