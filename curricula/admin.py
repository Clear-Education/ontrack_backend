from django.contrib import admin

# Register your models here.
from curricula.models import Carrera, Anio, Curso, Materia

# Register your models here.
admin.site.register(Carrera)
admin.site.register(Curso)
admin.site.register(Anio)
admin.site.register(Materia)
