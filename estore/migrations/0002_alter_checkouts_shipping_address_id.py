# Generated by Django 3.2.8 on 2021-11-05 12:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('estore', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkouts',
            name='shipping_address_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='estore.useraddress'),
        ),
    ]
