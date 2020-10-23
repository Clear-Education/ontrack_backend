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
    if objetivos:
        calculate_calificacion_redesign(objetivos, alumno, date_recalculate)


def calculate_calificacion_redesign(objetivos, alumno, date_recalculate):
    objetivos_ids = [o.id for o in objetivos]
    AlumnoObjetivo.objects.filter(
        objetivo__id__in=objetivos_ids,
        fecha_relacionada__gte=date_recalculate,
        alumno_curso__alumno__id=alumno,
    ).delete()

    materias = set(
        [
            m.id
            for objetivo in objetivos
            for m in objetivo.seguimiento.materias.all()
        ]
    )
    anio_lectivo = objetivos[0].seguimiento.anio_lectivo
    alumno_curso = [
        alumno_curso
        for alumno_curso in objetivos[0].seguimiento.alumnos.all()
        if alumno_curso.alumno.id == alumno
    ][0]

    calificaciones = Calificacion.objects.filter(
        alumno__exact=alumno_curso.alumno,
        evaluacion__anio_lectivo=anio_lectivo,
        evaluacion__materia__id__in=materias,
    ).order_by("fecha")

    for objetivo in objetivos:
        calculate_promedio_for_objetivo(
            objetivo, alumno_curso, date_recalculate, calificaciones
        )


def calculate_promedio_for_objetivo(
    objetivo, alumno_curso, date_recalculate, calificaciones
):
    materias = set([m.id for m in objetivo.seguimiento.materias.all()])

    fechas = sorted(
        list(
            {
                calificacion.fecha
                for calificacion in calificaciones
                if calificacion.fecha >= date_recalculate
                and calificacion.evaluacion.materia.id in materias
            }
        )
    )
    promedios = []

    for index in range(len(fechas)):
        calificaciones_fecha = [
            c for c in calificaciones if c.fecha <= fechas[index]
        ]
        calculate_for_date(
            calificaciones_fecha,
            materias,
            date_recalculate,
            fechas[index],
            objetivo,
            alumno_curso,
        )


def calculate_for_date(
    calificaciones_fecha,
    materias,
    date_recalculate,
    fechas,
    objetivo,
    alumno_curso,
):
    promedios = []
    calificaciones_materia = []
    for mat in materias:
        calificaciones_materia.append(
            [
                cal
                for cal in calificaciones_fecha
                if cal.evaluacion.materia.id == mat
            ]
        )

    promedios_ponderaciones = map(
        calculate_promedio_one_subject, calificaciones_materia
    )

    for nota, ponderacion in promedios_ponderaciones:
        promedios.append(
            nota + (1 - ponderacion) * objetivo.tipo_objetivo.valor_maximo
        )

    alumno_objetivo = AlumnoObjetivo(
        objetivo=objetivo,
        alumno_curso=alumno_curso,
        alcanzada=False,
        fecha_relacionada=fechas,
        valor=round(mean(promedios if promedios else [-1]), 2),
    )
    alumno_objetivo.save()


def calculate_promedio_one_subject(calificaciones_subject):
    promedio = 0
    ponderacion = 0

    for calificacion in calificaciones_subject:
        ponderacion += calificacion.evaluacion.ponderacion
        promedio += calificacion.evaluacion.ponderacion * calificacion.puntaje
    return promedio, ponderacion
