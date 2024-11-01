# Generated by Django 5.1.2 on 2024-11-01 13:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Carte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('niveau', models.PositiveIntegerField()),
                ('cout', models.JSONField(default=dict)),
                ('bonus', models.CharField(max_length=50)),
                ('points_victoire', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Partie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
                ('nombre_joueurs', models.IntegerField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('joueur_courant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parties_en_cours', to=settings.AUTH_USER_MODEL)),
                ('joueurs', models.ManyToManyField(related_name='parties', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='JoueurPartie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points_victoire', models.IntegerField(default=0)),
                ('jetons', models.JSONField(default=dict)),
                ('cartes_achetees', models.ManyToManyField(blank=True, related_name='achetees', to='jeu.carte')),
                ('cartes_reservees', models.ManyToManyField(blank=True, related_name='reservees', to='jeu.carte')),
                ('joueur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('partie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='jeu.partie')),
            ],
        ),
        migrations.CreateModel(
            name='Plateau',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cartes', models.ManyToManyField(related_name='plateaux', to='jeu.carte')),
                ('partie', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='plateau', to='jeu.partie')),
            ],
        ),
        migrations.CreateModel(
            name='Jeton',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('couleur', models.CharField(max_length=50)),
                ('quantite', models.PositiveIntegerField()),
                ('plateau', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='jetons', to='jeu.plateau')),
            ],
        ),
    ]
