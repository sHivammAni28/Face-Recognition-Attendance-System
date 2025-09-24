# Generated migration for adding face recognition field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='is_face_recognition',
            field=models.BooleanField(default=False, help_text='True if marked via face recognition'),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='session',
            field=models.CharField(
                choices=[
                    ('daily', 'Daily'),
                    ('morning', 'Morning'),
                    ('afternoon', 'Afternoon'),
                    ('evening', 'Evening')
                ],
                default='daily',
                max_length=10
            ),
        ),
    ]