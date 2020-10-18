from calificaciones.models import Calificacion
from seguimientos.models import Seguimiento
from objetivos.models import Objetivo, AlumnoObjetivo
from statistics import mean


def alumno_calificacion_redesign(alumno, materia, date_recalculate):

    objetivos = Objetivo.objects.filter(
        seguimiento__alumnos__alumno__id=alumno,
        seguimiento__en_progreso=True,
        seguimiento__anio_lectivo__fecha_desde__lte=date_recalculate,
        seguimiento__anio_lectivo__fecha_hasta__gte=date_recalculate,
        tipo_objetivo__nombre__icontains="Promedio",
        tipo_objetivo__cuantitativo=True,
        tipo_objetivo__multiple=False,
        seguimiento__materias__id=materia,
    )

    calculate_calificacion_redesign(objetivos, alumno, date_recalculate)


def calculate_calificacion_redesign(objetivos, alumno, date_recalculate):
    objetivos_ids = [o.id for o in objetivos]
    AlumnoObjetivo.objects.filter(
        objetivo__id__in=objetivos_ids,
        fecha_relacionada__gte=date_recalculate,
        alumno_curso__alumno__id=alumno,
    ).delete()

    for objetivo in objetivos:
        calculate_promedio_for_objetivo(objetivo, alumno, date_recalculate)


def calculate_promedio_for_objetivo(objetivo, alumno, date_recalculate):
    # anio_lectivo = objetivos[0].seguimiento.anio_lectivo
    # alumno_curso = [
    #     alumno_curso
    #     for alumno_curso in objetivos[0].seguimiento.alumnos.all()
    #     if alumno_curso.alumno.id == alumno
    # ][0]

    # create_datetime = timezone.now()

    # asistencias = Asistencia.objects.filter(
    #     fecha__gte=anio_lectivo.fecha_desde,
    #     fecha__lte=anio_lectivo.fecha_hasta,
    #     alumno_curso__alumno__id__exact=alumno,
    # ).order_by("fecha")

    # fechas = [
    #     asistencia.fecha
    #     for asistencia in asistencias
    #     if asistencia.fecha >= date_recalculate
    # ]

    # promedios = []

    # for index in reversed(range(len(asistencias))):
    #     if asistencias[index].fecha < date_recalculate:
    #         break
    #     promedio = mean([a.asistio for a in asistencias[: index + 1]])
    #     promedios.append(promedio)

    # objetivos_to_save = []

    # for fecha, promedio in zip(fechas, promedios[::-1]):
    #     for objetivo in objetivos:
    #         objetivos_to_save.append(
    #             AlumnoObjetivo(
    #                 fecha_calculo=create_datetime,
    #                 fecha_relacionada=fecha,
    #                 objetivo=objetivo,
    #                 alumno_curso=alumno_curso,
    #                 valor=promedio,
    #                 alcanzada=False,
    #             )
    #         )

    # AlumnoObjetivo.objects.bulk_create(objetivos_to_save)


def alumno_calificacion(alumno, materia):
    seguimientos = Seguimiento.objects.filter(
        alumnos__alumno__id=alumno, en_progreso=True, materias__id=materia
    ).distinct()
    for seguimiento in seguimientos:
        check_objetivos(seguimiento, alumno)


def check_objetivos(seguimiento, alumno):
    objetivo = Objetivo.objects.filter(
        seguimiento__exact=seguimiento,
        tipo_objetivo__nombre__icontains="promedio",
        tipo_objetivo__cuantitativo=True,
        tipo_objetivo__multiple=False,
    )
    if objetivo:
        calculate_promedio(objetivo[0], alumno)


def calculate_promedio(objetivo, alumno_id):
    materias = objetivo.seguimiento.materias.all()
    alumno_curso = objetivo.seguimiento.alumnos.get(
        alumno__id__exact=alumno_id
    )
    promedios_ponderaciones = map(
        calculate_promedio_one_subject,
        [(alumno_curso, materia) for materia in materias],
    )
    promedios_ponderaciones = [
        x for x in promedios_ponderaciones if x is not None
    ]
    promedios = list()
    for nota, ponderacion in promedios_ponderaciones:
        promedios.append(
            nota + (1 - ponderacion) * objetivo.tipo_objetivo.valor_maximo
        )
    alumno_objetivo = AlumnoObjetivo(
        objetivo=objetivo,
        alumno_curso=alumno_curso,
        alcanzada=False,
        valor=round(mean(promedios if promedios else [-1]), 2),
    )
    alumno_objetivo.save()


def calculate_promedio_one_subject(alumno_curso_materia):
    alumno_curso, materia = alumno_curso_materia
    calificaciones = Calificacion.objects.filter(
        alumno__exact=alumno_curso.alumno,
        evaluacion__anio_lectivo=alumno_curso.anio_lectivo,
        evaluacion__materia=materia,
    )
    if not calificaciones:
        return None
    promedio = 0
    ponderacion = 0
    for calificacion in calificaciones:
        ponderacion += calificacion.evaluacion.ponderacion
        promedio += calificacion.evaluacion.ponderacion * calificacion.puntaje
    return promedio, ponderacion
