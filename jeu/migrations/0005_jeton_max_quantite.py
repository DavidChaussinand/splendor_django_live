# Generated by Django 5.1.2 on 2024-11-05 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jeu', '0004_joueurpartie_cartes_achetees_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='jeton',
            name='max_quantite',
            field=models.IntegerField(default=7),
        ),
    ]