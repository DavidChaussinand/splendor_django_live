# Generated by Django 5.1.2 on 2024-10-30 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jeu', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='plateau',
            name='cartes',
            field=models.ManyToManyField(related_name='plateaux', to='jeu.carte'),
        ),
    ]
