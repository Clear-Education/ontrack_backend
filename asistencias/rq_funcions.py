from asistencias.models import Asistencia
from seguimientos.models import Seguimiento
from objetivos.models import Objetivo, AlumnoObjetivo
from django.db.models import Avg


def alumno_asistencia(alumno):
    seguimientos = Seguimiento.objects.filter(
        alumnos__alumno__id=alumno, en_progreso=True
    ).distinct()
    for seguimiento in seguimientos:
        check_objetivos(seguimiento, alumno)


def check_objetivos(seguimiento, alumno):
    objetivo = Objetivo.objects.filter(
        seguimiento__exact=seguimiento,
        tipo_objetivo__nombre__icontains="Asistencia",
        tipo_objetivo__cuantitativo=True,
        tipo_objetivo__multiple=False,
    )
    if objetivo:
        calculate_asistencia(objetivo[0], alumno)


def calculate_asistencia(objetivo, alumno_id):
    average = Asistencia.objects.filter(
        fecha__gte=objetivo.seguimiento.anio_lectivo.fecha_desde,
        fecha__lte=objetivo.seguimiento.anio_lectivo.fecha_hasta,
    ).aggregate(Avg("asistio"))
    average = average["asistio__avg"] if average["asistio__avg"] else 1
    alumno_curso = objetivo.seguimiento.alumnos.get(
        alumno__id__exact=alumno_id
    )
    alumno_objetivo = AlumnoObjetivo(
        objetivo=objetivo,
        alumno_curso=alumno_curso,
        alcanzada=False,
        valor=average,
    )
    alumno_objetivo.save()

