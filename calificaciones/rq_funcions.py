from calificaciones.models import Calificacion
from seguimientos.models import Seguimiento
from objetivos.models import Objetivo, AlumnoObjetivo
from statistics import mean


def alumno_calificacion(alumno, materia):
    seguimientos = Seguimiento.objects.filter(
        alumnos__alumno__id=alumno, en_progreso=True, materias__id=materia
    ).distinct()
    if seguimientos:
        map(check_objetivos, [(s, alumno) for s in seguimientos])


def check_objetivos(seguimiento_alumno):
    objetivo = Objetivo.objects.filter(
        seguimiento__exact=seguimiento_alumno[0],
        tipo_objetivo__nombre__icontains="Calific",
        tipo_objetivo__cuantitativo__equals=True,
        tipo_objetivo__multiple__exact=False,
    )
    if objetivo:
        calculate_promedio(objetivo[0], seguimiento_alumno[1])


def calculate_promedio(objetivo, alumno_id):
    materias = objetivo.seguimiento.materias.all()
    alumno_curso = objetivo.seguimiento.alumnos.get(
        alumno__id__exact=alumno_id
    )
    promedios_ponderaciones = map(
        calculate_promedio_one_subject,
        [(alumno_curso, materia) for materia in materias],
    )
    promedios_ponderaciones = [x for x in promedios if x is not None]
    promedios = list()
    for nota, ponderacion in promedios_ponderaciones:
        promedios.append(
            nota + (1 - ponderacion) * objetivo.tipo_objetivo.valor_maximo
        )

    alumno_objetivo = AlumnoObjetivo(
        objetivo=objetivo,
        alumno_curso=alumno_curso,
        alcanzada=False,
        valor=mean(promedios),
    )
    print(alumno_objetivo)
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
