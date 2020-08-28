from django.contrib import admin
from instituciones.models import Institucion
from django import forms


class InstitucionForm(forms.ModelForm):
    class Meta:
        model = Institucion
        fields = [
            "nombre",
            "direccion",
            "pais",
            "cuit",
            "identificador",
            "descripcion",
            "logo",
            "activa",
        ]

    def clean(self):
        cuit = self.cleaned_data.get("cuit")
        if not cuit:
            raise forms.ValidationError("Es necesario ingresar el CUIT")
        if len(Institucion.objects.filter(cuit__exact=cuit)) > 0:
            raise forms.ValidationError(
                "Ya existe una institución con dicho CUIT"
            )
        return self.cleaned_data


class InstitucionAdmin(admin.ModelAdmin):
    form = InstitucionForm


admin.site.register(Institucion, InstitucionAdmin)
