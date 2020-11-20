from django.contrib import admin
from objetivos.models import Objetivo, AlumnoObjetivo, TipoObjetivo
from ontrack import settings
from django import forms
from django.core.exceptions import ValidationError

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

    def clean(self):
        cleaned_data = super().clean()
        valor_minimo = cleaned_data.get("valor_minimo")
        valor_maximo = cleaned_data.get("valor_maximo")
        cuantitativo = cleaned_data.get("cuantitativo")

        if cuantitativo and not all([valor_maximo, valor_minimo]):
            raise ValidationError(
                "Es necesario ingresar un valor máximo y mínimo si el tipo es cuantitativo"
            )

        if valor_minimo and valor_maximo and not valor_maximo > valor_minimo:
            raise ValidationError("El valor máximo debe ser mayor al mínimo")


class TipoObjetivoAdmin(admin.ModelAdmin):
    form = TipoObjetivoForm


admin.site.register(TipoObjetivo, TipoObjetivoAdmin)
