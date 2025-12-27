from django.db import migrations, models
import pgvector.django

class Migration(migrations.Migration):
    dependencies = [
        ('rag', '0001_initial'),
    ]
    operations = [
        migrations.AddField(
            model_name='documentchunk',
            name='embedding',
            field=pgvector.django.VectorField(dimensions=768, null=True, blank=True, verbose_name='청크 임베딩'),
        ),
    ]
