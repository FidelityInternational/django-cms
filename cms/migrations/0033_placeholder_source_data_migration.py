# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-24 08:22
from __future__ import unicode_literals

from django.db import migrations


def forwards(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    ContentType = apps.get_model('contenttypes', 'ContentType')
    CMSPlugin = apps.get_model('cms', 'CMSPlugin')
    Placeholder = apps.get_model('cms', 'Placeholder')
    filtered_content_types = (
        ContentType
        .objects
        .using(db_alias)
        .exclude(app_label='cms', model__in=['cmsplugin', 'placeholder'])
    )

    for ct in filtered_content_types:
        model_class = apps.get_model(ct.app_label, ct.model)

        if issubclass(model_class, (CMSPlugin, Placeholder)):
            # We ignore all models inherited from CMSPlugin or Placeholder.
            continue

        # Get all fields which has a relationship to Placeholder.
        pl_related_fields = [
            f.name for f in model_class._meta.get_fields()
            if f.related_model == Placeholder and not f.auto_created
        ]

        if not pl_related_fields:
            # Model has no related fields with Placeholder.
            continue

        # Model has related field/s with Placeholder.
        # Now get all the objects for the model and populate source field.
        cur_ct_obj = ContentType.objects.get_for_model(model_class)

        for obj in model_class.objects.using(db_alias):
            for pl_field_name in pl_related_fields:
                pl_field = getattr(obj, pl_field_name)

                if pl_field.__class__.__name__ == 'ManyRelatedManager':
                    pl_field.update(
                        content_type_id=cur_ct_obj.pk,
                        object_id=obj.pk,
                    )
                else:
                    pl_field.content_type_id=cur_ct_obj.pk,
                    pl_field.object_id=obj.pk
                    obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0032_remove_title_to_pagecontent'),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
