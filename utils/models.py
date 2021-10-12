from django.db.models import DateTimeField, Model


class TimeStampModel(Model):
    # created datetime
    created = DateTimeField(auto_now_add=True, null=True)
    # updated datetime, that actualize each time the model is updated.
    updated = DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This model will then not be used to create any database table.
