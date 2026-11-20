from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(model_name="user", name="business_name", field=models.CharField(blank=True, max_length=150)),
        migrations.AddField(model_name="user", name="business_sector", field=models.CharField(blank=True, max_length=120)),
        migrations.AddField(model_name="user", name="business_stage", field=models.CharField(blank=True, max_length=80)),
        migrations.AddField(model_name="user", name="business_description", field=models.TextField(blank=True)),
        migrations.AddField(model_name="user", name="mentor_expertise", field=models.CharField(blank=True, max_length=200)),
        migrations.AddField(model_name="user", name="mentor_availability", field=models.CharField(blank=True, max_length=120)),
        migrations.AddField(model_name="user", name="investor_type", field=models.CharField(blank=True, max_length=80)),
        migrations.AddField(model_name="user", name="website", field=models.URLField(blank=True)),
    ]
