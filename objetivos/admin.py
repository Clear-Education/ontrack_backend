from django.contrib import admin
from objetivos.models import Objetivo, AlumnoObjetivo, TipoObjetivo
from ontrack import settings
from django import forms

if settings.DEVELOPER_ADMIN:
    admin.site.register(Objetivo)
    admin.site.register(AlumnoObjetivo)


class TipoObjetivoForm(forms.ModelForm):
    nombre = forms.CharField(max_length=150, required=True)
    descripcion = forms.CharField(max_length=150, required=True)
    cuantitativo = forms.BooleanField(required=False)
    multiple = forms.BooleanField(required=False)
    valor_minimo = forms.FloatField(required=False)
    valor_maximo = forms.FloatField(required=False)

    class Meta:
        model = TipoObjetivo
        fields = [
            "nombre",
            "descripcion",
            "cuantitativo",
            "multiple",
            "valor_minimo",
            "valor_maximo",
        ]


class TipoObjetivoAdmin(admin.ModelAdmin):
    form = TipoObjetivoForm


admin.site.register(TipoObjetivo, TipoObjetivoAdmin)
