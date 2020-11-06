from django import forms
from django.conf import settings
from .utils import backup_database, backup_media


class DatabaseBackupForm(forms.Form):
    database = forms.ChoiceField(
        label="Elija la Base de Datos",
        choices=zip(settings.DATABASES.keys(), settings.DATABASES.keys()),
    )

    def do_backup(self):
        return backup_database(self.cleaned_data["database"])


class MediaBackupForm(forms.Form):
    def do_backup(self):
        return backup_media()
