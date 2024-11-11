# Generated by Django 5.1.2 on 2024-11-11 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jeu', '0008_plateau_cartes_pile_niveau_2_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Noble',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
                ('points_de_victoire', models.PositiveIntegerField()),
                ('cout', models.JSONField(default=dict)),
            ],
        ),
        migrations.AddField(
            model_name='joueurpartie',
            name='nobles_acquis',
            field=models.ManyToManyField(blank=True, related_name='joueurs', to='jeu.noble'),
        ),
    ]