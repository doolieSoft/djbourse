# Generated by Django 3.1.3 on 2020-11-21 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bourse', '0003_transaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('symbol', models.CharField(max_length=5)),
            ],
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='nombre',
            new_name='quantity',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='cours',
            new_name='value',
        ),
        migrations.AddField(
            model_name='transaction',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='bourse.currency'),
        ),
    ]