# Generated by Django 5.1.2 on 2024-11-01 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jeu', '0003_remove_joueurpartie_cartes_achetees_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='joueurpartie',
            name='cartes_achetees',
            field=models.ManyToManyField(blank=True, related_name='achetees', to='jeu.carte'),
        ),
        migrations.AddField(
            model_name='joueurpartie',
            name='cartes_reservees',
            field=models.ManyToManyField(blank=True, related_name='reservees', to='jeu.carte'),
        ),
    ]
