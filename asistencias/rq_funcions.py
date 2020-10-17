from asistencias.models import Asistencia
from objetivos.models import Objetivo, AlumnoObjetivo
from statistics import mean
from django.utils import timezone


def alumno_asistencia_redesign(alumno, datetime_requested, date_recalculate):

    objetivos = Objetivo.objects.filter(
        seguimiento__alumnos__alumno__id=alumno,
        seguimiento__en_progreso=True,
        seguimiento__anio_lectivo__fecha_desde__lte=date_recalculate,
        seguimiento__anio_lectivo__fecha_hasta__gte=date_recalculate,
        tipo_objetivo__nombre__icontains="Asistencia",
        tipo_objetivo__cuantitativo=True,
        tipo_objetivo__multiple=False,
    )

    if should_recalculate(alumno, datetime_requested, objetivos):
        calculate_asistencia_redesign(objetivos, alumno, date_recalculate)


def should_recalculate(alumno, datetime_requested, objetivos):
    if not objetivos:
        return False

    alumno_objetivo = AlumnoObjetivo.objects.filter(
        objetivo__id__exact=objetivos[0].id,
        alumno_curso__alumno__id=alumno,
        fecha_calculo__isnull=False,
    ).order_by("-fecha_calculo")

    if (
        alumno_objetivo
        and alumno_objetivo[0].fecha_calculo > datetime_requested
    ):
        return False
    return True


def calculate_asistencia_redesign(objetivos, alumno, date_recalculate):
    objetivos_ids = [o.id for o in objetivos]
    AlumnoObjetivo.objects.filter(
        objetivo__id__in=objetivos_ids,
        fecha_relacionada__gte=date_recalculate,
        alumno_curso__alumno__id=alumno,
    ).delete()

    anio_lectivo = objetivos[0].seguimiento.anio_lectivo
    alumno_curso = [
        alumno_curso
        for alumno_curso in objetivos[0].seguimiento.alumnos.all()
        if alumno_curso.alumno.id == alumno
    ][0]

    create_datetime = timezone.now()

    asistencias = Asistencia.objects.filter(
        fecha__gte=anio_lectivo.fecha_desde,
        fecha__lte=anio_lectivo.fecha_hasta,
        alumno_curso__alumno__id__exact=alumno,
    ).order_by("fecha")

    fechas = [
        asistencia.fecha
        for asistencia in asistencias
        if asistencia.fecha >= date_recalculate
    ]

    promedios = []

    for index in reversed(range(len(asistencias))):
        if asistencias[index].fecha < date_recalculate:
            break
        promedio = mean([a.asistio for a in asistencias[: index + 1]])
        promedios.append(promedio)

    objetivos_to_save = []

    for fecha, promedio in zip(fechas, promedios[::-1]):
        for objetivo in objetivos:
            objetivos_to_save.append(
                AlumnoObjetivo(
                    fecha_calculo=create_datetime,
                    fecha_relacionada=fecha,
                    objetivo=objetivo,
                    alumno_curso=alumno_curso,
                    valor=promedio,
                    alcanzada=False,
                )
            )

    AlumnoObjetivo.objects.bulk_create(objetivos_to_save)
