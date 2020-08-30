from django.contrib import admin
from instituciones.models import Institucion
from curricula.models import Carrera
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib import messages
from django.http import HttpResponseRedirect


class InstitucionAdmin(admin.ModelAdmin):
    def message_user(self, *args):
        pass

    def delete_queryset(self, request, queryset):
        try:
            self._custom_queryset_delete(request, queryset)
        except ValidationError as err:
            msg = _(err.message)
            messages.add_message(request, messages.ERROR, msg)
            redirect_url = request.path
            return HttpResponseRedirect(redirect_url)

    def _custom_queryset_delete(self, request, queryset):
        instituciones = [i.pk for i in queryset]
        if (
            Carrera.objects.filter(institucion_id__in=instituciones).count()
            != 0
        ):
            raise ValidationError(
                message="No se pueden borrar instituciones, se perderá historial!"
            )
        queryset.delete()


admin.site.register(Institucion, InstitucionAdmin)
