# Generated by Django 3.1.3 on 2021-01-05 17:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0004_auto_20210104_1815'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_name', models.SlugField(unique=True)),
                ('name', models.CharField(blank=True, max_length=300, null=True)),
                ('conversation_type', models.PositiveSmallIntegerField(choices=[(1, 'Private'), (2, 'Group')])),
                ('user_type_creator', models.PositiveSmallIntegerField(choices=[(2, 'Admin'), (1, 'Applicant')])),
                ('user_creator', models.PositiveIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('closed', models.BooleanField(default=False)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ConversationParticipants',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_admin', models.BooleanField(default=False)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.conversation')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('message_type', models.PositiveSmallIntegerField(choices=[(1, 'Text'), (2, 'File'), (3, 'Emoji'), (4, 'Image'), (0, 'Other')])),
                ('delivered', models.BooleanField(default=False)),
                ('seen', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_conversation', to='registration.conversation')),
            ],
        ),
        migrations.AddField(
            model_name='applicant',
            name='english_notes',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='englishtest',
            name='notes',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.CreateModel(
            name='Participants',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_type', models.PositiveSmallIntegerField(choices=[(2, 'Admin'), (1, 'Applicant')])),
                ('user', models.PositiveIntegerField()),
                ('last_online', models.DateTimeField(blank=True, null=True)),
                ('is_online', models.BooleanField(default=False)),
                ('conversation', models.ManyToManyField(related_name='conversation_participants', through='registration.ConversationParticipants', to='registration.Conversation')),
            ],
            options={
                'unique_together': {('user_type', 'user')},
            },
        ),
        migrations.CreateModel(
            name='MessageParticipants',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiver', models.BooleanField(default=True)),
                ('seen', models.BooleanField(default=False)),
                ('delivered', models.BooleanField(default=False)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.message')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.participants')),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='participants',
            field=models.ManyToManyField(related_name='participants_message', through='registration.MessageParticipants', to='registration.Participants'),
        ),
        migrations.AddField(
            model_name='conversationparticipants',
            name='participant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.participants'),
        ),
    ]
