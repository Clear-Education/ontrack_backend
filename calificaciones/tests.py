from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from users.models import User, Group
from calificaciones.models import Calificacion
from instituciones.models import Institucion
from curricula.models import (
    Carrera,
    Anio,
    AnioLectivo,
    Evaluacion,
    Materia,
    Curso,
)
from django.contrib.auth.models import Permission
from alumnos.models import Alumno, AlumnoCurso
from rest_framework import status
from unittest.mock import patch
from seguimientos.models import Seguimiento
from curricula.models import Materia
from objetivos.models import Objetivo, TipoObjetivo, AlumnoObjetivo
import datetime
from calificaciones.rq_funcions import alumno_calificacion_redesign


class QueueCalificacionesTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup de User y permisos para poder ejecutar todas las acciones
        """
        cls.client = APIClient()
        cls.group_admin = Group.objects.create(name="Admin")
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can add asistencia")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can change asistencia")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can delete asistencia")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Puede listar asistencias")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can view asistencia")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Puede crear multiples asistencias")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Puede borrar multiples asistencias")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(
                name="Puede obtener el porcentaje de asistencias"
            )
        )
        cls.group_admin.save()

        cls.institucion_1 = Institucion.objects.create(
            nombre="Institucion_1", identificador="1234"
        )
        cls.institucion_1.save()

        cls.user_admin = User.objects.create_user(
            "admin@admin.com",
            password="password",
            groups=cls.group_admin,
            institucion=cls.institucion_1,
        )

        cls.carrera_1 = Carrera.objects.create(
            nombre="Carrera1",
            descripcion=".",
            institucion=cls.institucion_1,
            color=".",
        )

        cls.anio_1 = Anio.objects.create(
            nombre="Anio1", carrera=cls.carrera_1, color="."
        )

        cls.curso_1 = Curso.objects.create(nombre="Curso1", anio=cls.anio_1)

        cls.anio_lectivo_1 = AnioLectivo.objects.create(
            nombre="2019",
            fecha_desde="2019-01-01",
            fecha_hasta="2019-12-31",
            institucion=cls.institucion_1,
        )
        cls.anio_lectivo_1.save()

        cls.anio_lectivo_2 = AnioLectivo.objects.create(
            nombre="2020",
            fecha_desde="2020-01-01",
            fecha_hasta="2020-12-31",
            institucion=cls.institucion_1,
        )
        cls.anio_lectivo_2.save()

        cls.alumno_1 = Alumno.objects.create(
            dni=1,
            nombre="Alumno",
            apellido="1",
            institucion=cls.institucion_1,
        )
        cls.alumno_1.save()

        cls.alumno_2 = Alumno.objects.create(
            dni=2,
            nombre="Alumno",
            apellido="2",
            institucion=cls.institucion_1,
        )
        cls.alumno_2.save()

        cls.alumno_curso_1 = AlumnoCurso.objects.create(
            alumno=cls.alumno_1,
            curso=cls.curso_1,
            anio_lectivo=cls.anio_lectivo_1,
        )
        cls.alumno_curso_1.save()

        cls.alumno_curso_2 = AlumnoCurso.objects.create(
            alumno=cls.alumno_1,
            curso=cls.curso_1,
            anio_lectivo=cls.anio_lectivo_2,
        )
        cls.alumno_curso_2.save()

        cls.alumno_curso_3 = AlumnoCurso.objects.create(
            alumno=cls.alumno_2,
            curso=cls.curso_1,
            anio_lectivo=cls.anio_lectivo_1,
        )
        cls.alumno_curso_3.save()

        cls.alumno_curso_4 = AlumnoCurso.objects.create(
            alumno=cls.alumno_2,
            curso=cls.curso_1,
            anio_lectivo=cls.anio_lectivo_2,
        )
        cls.alumno_curso_4.save()

        cls.materia_1 = Materia.objects.create(
            nombre="Matematicas", anio=cls.anio_1
        )
        cls.materia_1.save()

        cls.materia_2 = Materia.objects.create(
            nombre="Lengua", anio=cls.anio_1
        )
        cls.materia_2.save()

        cls.evaluacion_1 = Evaluacion.objects.create(
            nombre="Evaluacion Mat 1",
            materia=cls.materia_1,
            anio_lectivo=cls.anio_lectivo_1,
            ponderacion=0.3,
        )
        cls.evaluacion_2 = Evaluacion.objects.create(
            nombre="Evaluacion Mat 2",
            materia=cls.materia_1,
            anio_lectivo=cls.anio_lectivo_1,
            ponderacion=0.7,
        )
        cls.evaluacion_3 = Evaluacion.objects.create(
            nombre="Evaluacion Mat 1 otro anio",
            materia=cls.materia_1,
            anio_lectivo=cls.anio_lectivo_2,
            ponderacion=1,
        )
        cls.evaluacion_4 = Evaluacion.objects.create(
            nombre="Evaluacion Lengua 1",
            materia=cls.materia_2,
            anio_lectivo=cls.anio_lectivo_1,
            ponderacion=1,
        )

        cls.calificacion_1 = Calificacion.objects.create(
            fecha=datetime.date(2019, 3, 4),
            puntaje=80,
            alumno=cls.alumno_1,
            evaluacion=cls.evaluacion_1,
        )
        cls.calificacion_2 = Calificacion.objects.create(
            fecha=datetime.date(2019, 3, 5),
            puntaje=50,
            alumno=cls.alumno_1,
            evaluacion=cls.evaluacion_4,
        )
        cls.calificacion_3 = Calificacion.objects.create(
            fecha=datetime.date(2020, 3, 4),
            puntaje=10,
            alumno=cls.alumno_1,
            evaluacion=cls.evaluacion_3,
        )

        cls.seguimiento_1 = Seguimiento.objects.create(
            nombre="seguimiento_1",
            en_progreso=True,
            institucion=cls.institucion_1,
            fecha_inicio=datetime.date(2019, 1, 1),
            fecha_cierre=datetime.date(2019, 12, 31),
            descripcion=".",
            anio_lectivo=cls.anio_lectivo_1,
        )
        cls.seguimiento_1.alumnos.add(cls.alumno_curso_1, cls.alumno_curso_3)
        cls.seguimiento_1.materias.add(cls.materia_1, cls.materia_2)
        cls.seguimiento_1.save()

        cls.tipo_objetivo_1 = TipoObjetivo.objects.create(
            nombre="Cualitativo", cuantitativo=False, multiple=True,
        )
        cls.tipo_objetivo_2 = TipoObjetivo.objects.create(
            nombre="Promedio calificaciones",
            cuantitativo=True,
            multiple=False,
            valor_minimo=0,
            valor_maximo=100,
        )
        cls.tipo_objetivo_3 = TipoObjetivo.objects.create(
            nombre="Porcentaje asistencias",
            cuantitativo=True,
            multiple=False,
            valor_minimo=0,
            valor_maximo=100,
        )

        cls.objetivo_1 = Objetivo.objects.create(
            descripcion="conducta",
            seguimiento=cls.seguimiento_1,
            tipo_objetivo=cls.tipo_objetivo_1,
        )
        cls.objetivo_2 = Objetivo.objects.create(
            valor_objetivo_cuantitativo=70,
            seguimiento=cls.seguimiento_1,
            tipo_objetivo=cls.tipo_objetivo_2,
        )
        cls.objetivo_3 = Objetivo.objects.create(
            valor_objetivo_cuantitativo=70,
            seguimiento=cls.seguimiento_1,
            tipo_objetivo=cls.tipo_objetivo_3,
        )

    def test_objetivos_queue(self):
        """
        Test de creacion correcta de AlumnoObjetivos
        """

        alumno_calificacion_redesign(
            self.alumno_1.id, self.materia_1.id, datetime.date(2019, 3, 4)
        )

        alumnos_objetivos = AlumnoObjetivo.objects.all()
        assert alumnos_objetivos[0].valor == 97
        assert alumnos_objetivos[1].valor == 72

        self.calificacion_4 = Calificacion.objects.create(
            fecha=datetime.date(2019, 3, 6),
            puntaje=50,
            alumno=self.alumno_1,
            evaluacion=self.evaluacion_2,
        )

        alumno_calificacion_redesign(
            self.alumno_1.id, self.materia_2.id, datetime.date(2019, 3, 6)
        )
        alumnos_objetivos = AlumnoObjetivo.objects.all()
        assert alumnos_objetivos[0].valor == 97
        assert alumnos_objetivos[1].valor == 72
        assert alumnos_objetivos[2].valor == 54.5

        calif = Calificacion.objects.get(
            fecha__exact=datetime.date(2019, 3, 5), puntaje__exact=50,
        )
        calif.puntaje = 85
        calif.save()

        alumno_calificacion_redesign(
            self.alumno_1.id, self.materia_2.id, calif.fecha
        )
        alumnos_objetivos = AlumnoObjetivo.objects.all()
        assert alumnos_objetivos[0].valor == 97
        assert alumnos_objetivos[1].valor == 89.5
        assert alumnos_objetivos[2].valor == 72

        # Calificacion.objects.all().delete()
        # alumno_calificacion_redesign(
        #     self.alumno_1.id, self.materia_1.id, datetime.date(2019, 3, 4)
        # )
        # alumnos_objetivos = AlumnoObjetivo.objects.all()
        # assert alumnos_objetivos[0].valor == -1


@patch("calificaciones.api.views.django_rq")
class MateriaEvaluacionTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup de User y permisos para poder ejecutar todas las acciones
        """
        cls.client = APIClient()
        cls.group = Group.objects.create(name="Superadmin")
        cls.group.permissions.add(
            *Permission.objects.values_list("id", flat=True)
        )
        cls.institucion = Institucion.objects.create(
            nombre="MIT", identificador="12345"
        )

        cls.carrera = Carrera.objects.create(
            **{
                "nombre": "Ingenieria en Creatividad",
                "institucion_id": cls.institucion.pk,
            }
        )
        cls.anio = Anio.objects.create(
            **{"nombre": "1er Año", "carrera_id": cls.carrera.pk}
        )
        cls.curso = Curso.objects.create(**{"nombre": "1A", "anio": cls.anio})
        Curso.objects.create(**{"nombre": "2A", "anio": cls.anio})
        cls.anio_lectivo = AnioLectivo.objects.create(
            **{
                "nombre": "2020/2021",
                "fecha_desde": "2020-12-12",
                "fecha_hasta": "2021-12-12",
                "institucion": cls.institucion,
            }
        )
        cls.materia = Materia.objects.create(
            **{"nombre": "Análisis Matemático", "anio_id": cls.anio.pk}
        )
        cls.materia1 = Materia.objects.create(
            **{"nombre": "Econometrics", "anio_id": cls.anio.pk}
        )

        cls.evaluacion1 = Evaluacion.objects.create(
            **{
                "anio_lectivo": cls.anio_lectivo,
                "nombre": "evaluacion 1",
                "materia": cls.materia,
                "ponderacion": 0.5,
            }
        )
        cls.evaluacion1.save()
        cls.evaluacion11 = Evaluacion.objects.create(
            **{
                "anio_lectivo": cls.anio_lectivo,
                "materia": cls.materia1,
                "ponderacion": 1,
                "nombre": "evaluacion 11",
            }
        )
        cls.evaluacion2 = Evaluacion.objects.create(
            **{
                "anio_lectivo": cls.anio_lectivo,
                "materia": cls.materia,
                "ponderacion": 0.3,
                "nombre": "evaluacion 2",
            }
        )
        cls.evaluacion3 = Evaluacion.objects.create(
            **{
                "anio_lectivo": cls.anio_lectivo,
                "materia": cls.materia,
                "ponderacion": 0.2,
                "nombre": "evaluacion 3",
            }
        )
        # Institucion 2
        cls.institucion2 = Institucion.objects.create(
            nombre="SNU", identificador="12354"
        )
        cls.anio_lectivo2 = AnioLectivo.objects.create(
            **{
                "nombre": "2020/2021",
                "fecha_desde": "2020-12-12",
                "fecha_hasta": "2021-12-12",
                "institucion": cls.institucion2,
            }
        )
        cls.carrera2 = Carrera.objects.create(
            **{
                "nombre": "Ingenieria en Creatividad",
                "institucion_id": cls.institucion2.pk,
            }
        )
        cls.anio2 = Anio.objects.create(
            **{"nombre": "1er Año", "carrera_id": cls.carrera2.pk}
        )
        cls.curso2 = Curso.objects.create(
            **{"nombre": "1A", "anio": cls.anio2}
        )
        cls.materia2 = Materia.objects.create(
            **{"nombre": "Análisis Matemático", "anio_id": cls.anio2.pk}
        )

        cls.evaluacion_alt = Evaluacion.objects.create(
            **{
                "anio_lectivo": cls.anio_lectivo2,
                "materia": cls.materia2,
                "ponderacion": 1,
                "nombre": "Evaluacion 1",
            }
        )
        # Alumnos
        cls.alumno1 = Alumno.objects.create(
            dni=1,
            nombre="Alumno",
            apellido="Alume",
            institucion=cls.institucion,
        )
        cls.alumno_curso1 = AlumnoCurso.objects.create(
            alumno=cls.alumno1, curso=cls.curso, anio_lectivo=cls.anio_lectivo,
        )
        cls.alumno2 = Alumno.objects.create(
            dni=2,
            nombre="Alumno",
            apellido="Aluma",
            institucion=cls.institucion,
        )
        cls.alumno_curso2 = AlumnoCurso.objects.create(
            alumno=cls.alumno2, curso=cls.curso, anio_lectivo=cls.anio_lectivo,
        )
        cls.alumno3 = Alumno.objects.create(
            dni=3,
            nombre="Alumno",
            apellido="Alum",
            institucion=cls.institucion,
        )
        cls.alumno_curso3 = AlumnoCurso.objects.create(
            alumno=cls.alumno3, curso=cls.curso, anio_lectivo=cls.anio_lectivo,
        )
        cls.alumno4 = Alumno.objects.create(
            dni=4,
            nombre="Alumno",
            apellido="Alum",
            institucion=cls.institucion2,
        )

        cls.user = User.objects.create_user(
            "juan@juan.com",
            password="juan123",
            groups=cls.group,
            institucion=cls.institucion,
        )

    def setUp(self):
        """
            Fuerzo la autenticacion en cada corrida
        """
        self.client.force_authenticate(user=self.user)

    def test_create_multiples_calificaciones(self, mock):
        """
        Test de creacion de calificaciones para un curso y una evaluacion
        """
        url = "/api/calificaciones/multiple/"
        data = {
            "evaluacion": self.evaluacion1.pk,
            "fecha": "2020-12-12",
            "calificaciones": [
                {"alumno": self.alumno1.pk, "puntaje": 10},
                {"alumno": self.alumno2.pk, "puntaje": 7},
                {"alumno": self.alumno3.pk, "puntaje": 9},
            ],
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Calificacion.objects.count(), 3)

    def test_create_invalid_multiples_calificaciones(self, mock):
        """
        Test de creacion de calificaciones para un curso y una evaluacion
        """
        url = "/api/calificaciones/multiple/"
        data = {
            "fecha": "2020-12-12",
            "calificaciones": [
                {"alumno": self.alumno1.pk, "puntaje": 10},
                {"alumno": self.alumno2.pk, "puntaje": 7},
                {"alumno": self.alumno3.pk, "puntaje": 9},
            ],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Calificacion.objects.count(), 0)
        data = {
            "fecha": "2020-12-12",
            "calificaciones": [
                {"alumno": self.alumno1.pk, "puntaje": 10},
                {"alumno": self.alumno4.pk, "puntaje": 7},
                {"alumno": self.alumno3.pk, "puntaje": 9},
            ],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Calificacion.objects.count(), 0)

    def test_create_single_calificaciones(self, mock):
        """
        Test de creacion de calificaciones para un curso y una evaluacion
        """
        url = "/api/calificaciones/"
        data = {
            "evaluacion": self.evaluacion1.pk,
            "fecha": "2020-12-12",
            "alumno": self.alumno1.pk,
            "puntaje": 10,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Calificacion.objects.count(), 1)

    def test_create_invalid_single_calificaciones(self, mock):
        """
        Test de creacion de calificaciones para un curso y una evaluacion
        """
        url = "/api/calificaciones/"
        data = {
            "evaluacion": self.evaluacion1.pk,
            "alumno": self.alumno1.pk,
            "puntaje": 10,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Calificacion.objects.count(), 0)
        data = {
            "evaluacion": self.evaluacion1.pk,
            "alumno": self.alumno1.pk,
            "fecha": "2020-12-12",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Calificacion.objects.count(), 0)
        data = {
            "fecha": "2020-12-12",
            "alumno": self.alumno1.pk,
            "puntaje": 10,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Calificacion.objects.count(), 0)
        data = {
            "evaluacion": 9,
            "fecha": "2020-12-12",
            "alumno": self.alumno1.pk,
            "puntaje": 10,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Calificacion.objects.count(), 0)

    def test_edit_single_calificaciones(self, mock):
        """
        Test de edición de una calificacion, edicion correcta
        """
        calificacion = Calificacion.objects.create(
            alumno=self.alumno1,
            evaluacion=self.evaluacion1,
            fecha="2020-12-12",
            puntaje=9,
        )
        calificacion.save()
        url = "/api/calificaciones/{}/".format(calificacion.pk)
        data = {"puntaje": 10, "fecha": "2020-10-12"}

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Calificacion.objects.count(), 1)
        c = Calificacion.objects.first()
        self.assertEqual(c.puntaje, 10)
        fecha = c.fecha.strftime("%Y-%m-%d")
        self.assertEqual(fecha, "2020-10-12")

    def test_edit_invalid_puntaje_single_calificaciones(self, mock):
        """
        Test de edición de una calificacion, puntaje invalido
        """
        calificacion = Calificacion.objects.create(
            alumno=self.alumno1,
            evaluacion=self.evaluacion1,
            fecha="2020-12-12",
            puntaje=9,
        )
        calificacion.save()
        url = "/api/calificaciones/{}/".format(calificacion.pk)
        data = {"puntaje": "", "fecha": "2020-10-12"}

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        c = Calificacion.objects.first()
        self.assertEqual(c.puntaje, 9)
        fecha = c.fecha.strftime("%Y-%m-%d")
        self.assertEqual(fecha, "2020-12-12")

    def test_edit_invalid_fecha_single_calificaciones(self, mock):
        """
        Test de edición de una calificacion, formato de fecha
        """
        calificacion = Calificacion.objects.create(
            alumno=self.alumno1,
            evaluacion=self.evaluacion1,
            fecha="2020-12-12",
            puntaje=9,
        )
        calificacion.save()
        url = "/api/calificaciones/{}/".format(calificacion.pk)
        data = {"fecha": "2020-14-12"}

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        c = Calificacion.objects.first()
        fecha = c.fecha.strftime("%Y-%m-%d")
        self.assertEqual(fecha, "2020-12-12")

    def test_edit_alumno_no_effect_single_calificaciones(self, mock):
        """
        Test de edición de una calificacion, no debe editarse la FK alumno
        """
        calificacion = Calificacion.objects.create(
            alumno=self.alumno1,
            evaluacion=self.evaluacion1,
            fecha="2020-12-12",
            puntaje=9,
        )
        calificacion.save()
        url = "/api/calificaciones/{}/".format(calificacion.pk)
        data = {"fecha": "2020-12-13", "alumno": self.alumno2.pk}

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = Calificacion.objects.first()
        fecha = c.fecha.strftime("%Y-%m-%d")

        self.assertEqual(fecha, "2020-12-13")
        self.assertEqual(c.alumno_id, self.alumno1.pk)

    def test_edit_evaluacion_no_effect_single_calificaciones(self, mock):
        """
        Test de edición de una calificacion, no debe editarse la FK alumno
        """
        calificacion = Calificacion.objects.create(
            alumno=self.alumno1,
            evaluacion=self.evaluacion1,
            fecha="2020-12-12",
            puntaje=9,
        )
        calificacion.save()
        url = "/api/calificaciones/{}/".format(calificacion.pk)
        data = {"fecha": "2020-12-13", "evaluacion": self.evaluacion2.pk}

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = Calificacion.objects.first()
        fecha = c.fecha.strftime("%Y-%m-%d")
        self.assertEqual(fecha, "2020-12-13")
        self.assertEqual(c.evaluacion_id, self.evaluacion1.pk)

    def test_delete_single_calificaciones(self, mock):
        """
        Test para eliminacion de una calificacion
        """
        calificacion = Calificacion.objects.create(
            alumno=self.alumno1,
            evaluacion=self.evaluacion1,
            fecha="2020-12-12",
            puntaje=9,
        )
        calificacion.save()
        url = "/api/calificaciones/{}/".format(calificacion.pk)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Calificacion.objects.count(), 0)

    def test_delete_non_existent_single_calificaciones(self, mock):
        """
        Test para eliminacion de una calificacion
        """
        calificacion = Calificacion.objects.create(
            alumno=self.alumno1,
            evaluacion=self.evaluacion1,
            fecha="2020-12-12",
            puntaje=9,
        )
        calificacion.save()
        url = "/api/calificaciones/{}/".format(calificacion.pk + 1)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Calificacion.objects.count(), 1)

    def test_delete_different_institucion_single_calificaciones(self, mock):
        """
        Test para eliminacion de una calificacion
        """
        calificacion = Calificacion.objects.create(
            alumno=self.alumno1,
            evaluacion=self.evaluacion1,
            fecha="2020-12-12",
            puntaje=9,
        )
        calificacion2 = Calificacion.objects.create(
            alumno=self.alumno4,
            evaluacion=self.evaluacion_alt,
            fecha="2020-10-12",
            puntaje=9,
        )
        calificacion.save()
        calificacion2.save()
        url = "/api/calificaciones/{}/".format(calificacion2.pk)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Calificacion.objects.count(), 2)

    def test_delete_multiple_calificaciones(self, mock):
        """
        Test para eliminacion de multiples
        """
        calificaciones = [
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno4.pk,
                "evaluacion_id": self.evaluacion_alt.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
        ]
        for calificacion in calificaciones:
            calificacion = Calificacion.objects.create(**calificacion)
            calificacion.save()
        data = {"curso": self.curso.pk, "evaluacion": self.evaluacion1.pk}
        url = "/api/calificaciones/multiple/"

        response = self.client.delete(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Calificacion.objects.count(), 1)

    """
    Casos de uso listar calificaciones:
        Ver calificaciones de un curso para una evaluacion
        Ver calificaciones de un alumno para un materia en un año lectivo
        Ver calificaciones de un alumno para un año lectivo
    """

    def test_list_curso_evaluacion_calificaciones(self, mock):
        """
        Test para listar calificaciones segun curso y evaluacion
        """
        calificaciones = [
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno4.pk,
                "evaluacion_id": self.evaluacion_alt.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
        ]
        for calificacion in calificaciones:
            calificacion = Calificacion.objects.create(**calificacion)
            calificacion.save()
        url = "/api/calificaciones/list/?evaluacion={}&curso={}".format(
            self.evaluacion1.pk, self.curso.pk
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_list_alumno_materia_aniolectivo_calificaciones(self, mock):
        """
        Test para listar calificaciones segun alumno, materia y año_lectivo
        """
        calificaciones = [
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 7,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion3.pk,
                "fecha": "2020-12-12",
                "puntaje": 8,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno4.pk,
                "evaluacion_id": self.evaluacion_alt.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
        ]
        for calificacion in calificaciones:
            calificacion = Calificacion.objects.create(**calificacion)
            calificacion.save()
        url = "/api/calificaciones/list/?alumno={}&materia={}&anio_lectivo={}".format(
            self.alumno1.pk, self.materia.pk, self.anio_lectivo.pk
        )

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
        prom = 0
        for r in response.data["results"]:
            prom += r["puntaje"]
        prom = prom / len(response.data["results"])
        self.assertEqual(prom, 8)

    def test_list_alumno_aniolectivo_calificaciones(self, mock):
        """
        Test para listar calificaciones segun alumno y año_lectivo
        """
        calificaciones = [
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 7,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion11.pk,
                "fecha": "2020-12-12",
                "puntaje": 10,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion3.pk,
                "fecha": "2020-12-12",
                "puntaje": 8,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno4.pk,
                "evaluacion_id": self.evaluacion_alt.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
        ]
        for calificacion in calificaciones:
            calificacion = Calificacion.objects.create(**calificacion)
            calificacion.save()
        url = "/api/calificaciones/list/?alumno={}&anio_lectivo={}".format(
            self.alumno1.pk, self.anio_lectivo.pk
        )

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)

    def test_list_invalid_alumno_aniolectivo_calificaciones(self, mock):
        """
        Test para listar calificaciones segun alumno y año_lectivo
        Alumno de otra institucion
        """
        calificaciones = [
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 7,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion11.pk,
                "fecha": "2020-12-12",
                "puntaje": 10,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion3.pk,
                "fecha": "2020-12-12",
                "puntaje": 8,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno4.pk,
                "evaluacion_id": self.evaluacion_alt.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
        ]
        for calificacion in calificaciones:
            calificacion = Calificacion.objects.create(**calificacion)
            calificacion.save()
        url = "/api/calificaciones/list/?alumno={}&anio_lectivo={}".format(
            self.alumno4.pk, self.anio_lectivo.pk
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_without_alumno_aniolectivo_calificaciones(self, mock):
        """
        Test para listar calificaciones segun alumno y año_lectivo
        param alumno faltante
        """
        url = "/api/calificaciones/list/?anio_lectivo={}".format(
            self.anio_lectivo.pk
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Es necesario especificar el id del alumno",
        )

    def test_list_alumno_without_aniolectivo_calificaciones(self, mock):
        """
        Test para listar calificaciones segun alumno y año_lectivo
        param año_lectivo faltante
        """
        url = "/api/calificaciones/list/?alumno={}".format(self.alumno4.pk)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Es necesario especificar el id del anio_lectivo",
        )

    def test_list_curso_without_evaluacion_calificaciones(self, mock):
        """
        Test para listar calificaciones segun curso y evaluacion
        param evaluacion faltante
        """
        url = "/api/calificaciones/list/?curso={}".format(self.curso.pk)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Es necesario especificar el id de la evaluacion",
        )

    def test_list_without_curso_evaluacion_calificaciones(self, mock):
        """
        Test para listar calificaciones segun curso y evaluacion
        param curso faltante
        """
        url = "/api/calificaciones/list/?evaluacion={}".format(
            self.evaluacion1.pk
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Es necesario especificar el id del curso",
        )

    def test_list_alumno_materia_without_aniolectivo_calificaciones(
        self, mock
    ):
        """
        Test para listar calificaciones segun alumno materia y anio_lectivo
        param anio_lectivo faltante
        """
        url = "/api/calificaciones/list/?alumno={}&materia={}".format(
            self.alumno1.pk, self.materia.pk
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Es necesario especificar el id del anio_lectivo",
        )

    def test_list_without_alumno_materia_aniolectivo_calificaciones(
        self, mock
    ):
        """
        Test para listar calificaciones segun alumno materia y anio_lectivo
        param materia faltante
        """
        url = "/api/calificaciones/list/?materia={}&anio_lectivo={}".format(
            self.materia.pk, self.anio_lectivo.pk
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Es necesario especificar el id del alumno",
        )

    def test_promedio_alumno_aniolectivo_calificaciones(self, mock):
        """
        Test para obtener el promedio de calificaciones segun alumno y año_lectivo
        Se debe recibir un promedio por cada materia y un promedio general del año lectivo
        """
        calificaciones = [
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 7,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion11.pk,
                "fecha": "2020-12-12",
                "puntaje": 10,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion3.pk,
                "fecha": "2020-12-12",
                "puntaje": 8,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno4.pk,
                "evaluacion_id": self.evaluacion_alt.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
        ]
        for calificacion in calificaciones:
            calificacion = Calificacion.objects.create(**calificacion)
            calificacion.save()
        url = "/api/calificaciones/stats/promedio/?alumno={}&anio_lectivo={}".format(
            self.alumno1.pk, self.anio_lectivo.pk
        )

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data["promedios"]), list)

        for p in response.data["promedios"]:
            self.assertIn("nombre_materia", p)
            self.assertIn("promedio", p)
            if (
                p["nombre_materia"] == "ANÁLISIS MATEMÁTICO"
                or p["nombre_materia"] == "ECONOMETRICS"
            ):
                if p["nombre_materia"] == "ANÁLISIS MATEMÁTICO":
                    self.assertEqual(p["promedio"], 8)
                elif p["nombre_materia"] == "ECONOMETRICS":
                    self.assertEqual(p["promedio"], 10)
            else:
                self.assertEqual(True, False)
        self.assertEqual(response.data["alumno"], self.alumno1.pk)
        self.assertEqual(response.data["promedio_general"], 9)

    def test_promedio_alumno_materia_aniolectivo_calificaciones(self, mock):
        """
        Test para obtener el promedio de calificaciones segun alumno, materia y año_lectivo
        Se debe recibir el promedio del alumno en la materia
        """
        calificaciones = [
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 7,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion11.pk,
                "fecha": "2020-12-12",
                "puntaje": 10,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion3.pk,
                "fecha": "2020-12-12",
                "puntaje": 8,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno4.pk,
                "evaluacion_id": self.evaluacion_alt.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
        ]
        for calificacion in calificaciones:
            calificacion = Calificacion.objects.create(**calificacion)
            calificacion.save()
        url = "/api/calificaciones/stats/promedio/?alumno={}&anio_lectivo={}&materia={}".format(
            self.alumno1.pk, self.anio_lectivo.pk, self.materia.pk
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for p in response.data["promedios"]:
            self.assertIn("nombre_materia", p)
            self.assertIn("promedio", p)
            self.assertEqual(p["nombre_materia"], "ANÁLISIS MATEMÁTICO")
            self.assertEqual(p["promedio"], 8.0)

        self.assertNotIn("promedio_general", response.data)

        self.assertEqual(response.data["alumno"], self.alumno1.pk)

    def test_promedio_missing_alumno_calificaciones(self, mock):
        """
        Test para obtener el promedio de calificaciones segun alumno, materia y año_lectivo
        Debe verificar que el alumno no se pasó y emitir el error
        """

        url = "/api/calificaciones/stats/promedio/?&anio_lectivo={}&materia={}".format(
            self.anio_lectivo.pk, self.materia.pk
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Es necesario especificar el id del alumno",
        )

    def test_promedio_missing_aniolectivo_calificaciones(self, mock):
        """
        Test para obtener el promedio de calificaciones segun alumno, materia y año_lectivo
        Debe verificar que el alumno no se pasó y emitir el error
        """

        url = "/api/calificaciones/stats/promedio/?&alumno={}&materia={}".format(
            self.alumno1.pk, self.materia.pk
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Es necesario especificar el id del anio_lectivo",
        )

    # Nota FINAL
    def test_notafinal_alumno_aniolectivo_calificaciones(self, mock):
        """
        Test para obtener la nota final de calificaciones segun alumno y año_lectivo
        Se debe recibir una nota final por cada materia y un promedio general del año lectivo
        """
        calificaciones = [
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 7,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion11.pk,
                "fecha": "2020-12-12",
                "puntaje": 10,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion3.pk,
                "fecha": "2020-12-12",
                "puntaje": 8,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno4.pk,
                "evaluacion_id": self.evaluacion_alt.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
        ]
        for calificacion in calificaciones:
            calificacion = Calificacion.objects.create(**calificacion)
            calificacion.save()
        url = "/api/calificaciones/stats/nota-final/?alumno={}&anio_lectivo={}".format(
            self.alumno1.pk, self.anio_lectivo.pk
        )

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data["notas_finales"]), list)

        for p in response.data["notas_finales"]:
            self.assertIn("nombre_materia", p)
            self.assertIn("nota_final", p)
            if (
                p["nombre_materia"] == "ANÁLISIS MATEMÁTICO"
                or p["nombre_materia"] == "ECONOMETRICS"
            ):
                if p["nombre_materia"] == "ANÁLISIS MATEMÁTICO":
                    self.assertEqual(
                        p["nota_final"], 9 * 0.5 + 7 * 0.3 + 8 * 0.2
                    )
                elif p["nombre_materia"] == "ECONOMETRICS":
                    self.assertEqual(p["nota_final"], 10)
            else:
                self.assertEqual(True, False)
        self.assertEqual(response.data["alumno"], self.alumno1.pk)
        self.assertEqual(response.data["promedio_general"], 9.1)

    def test_notafinal_alumno_materia_aniolectivo_calificaciones(self, mock):
        """
        Test para obtener la nota final de calificaciones segun alumno, materia y año_lectivo
        Se debe recibir la nota final del alumno en la materia
        """
        calificaciones = [
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 7,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion11.pk,
                "fecha": "2020-12-12",
                "puntaje": 10,
            },
            {
                "alumno_id": self.alumno1.pk,
                "evaluacion_id": self.evaluacion3.pk,
                "fecha": "2020-12-12",
                "puntaje": 8,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno2.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion2.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno3.pk,
                "evaluacion_id": self.evaluacion1.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
            {
                "alumno_id": self.alumno4.pk,
                "evaluacion_id": self.evaluacion_alt.pk,
                "fecha": "2020-12-12",
                "puntaje": 9,
            },
        ]
        for calificacion in calificaciones:
            calificacion = Calificacion.objects.create(**calificacion)
            calificacion.save()
        url = "/api/calificaciones/stats/nota-final/?alumno={}&anio_lectivo={}&materia={}".format(
            self.alumno1.pk, self.anio_lectivo.pk, self.materia.pk
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for p in response.data["notas_finales"]:
            self.assertIn("nombre_materia", p)
            self.assertIn("nota_final", p)
            self.assertEqual(p["nombre_materia"], "ANÁLISIS MATEMÁTICO")
            self.assertEqual(p["nota_final"], 8.2)

        self.assertNotIn("promedio_general", response.data)

        self.assertEqual(response.data["alumno"], self.alumno1.pk)

    def test_notafinal_missing_alumno_calificaciones(self, mock):
        """
        Test para obtener la nota final de calificaciones segun alumno, materia y año_lectivo
        Debe verificar que el alumno no se pasó y emitir el error
        """

        url = "/api/calificaciones/stats/nota-final/?&anio_lectivo={}&materia={}".format(
            self.anio_lectivo.pk, self.materia.pk
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Es necesario especificar el id del alumno",
        )

    def test_notafinal_missing_aniolectivo_calificaciones(self, mock):
        """
        Test para obtener la nota final de calificaciones segun alumno, materia y año_lectivo
        Debe verificar que el alumno no se pasó y emitir el error
        """

        url = "/api/calificaciones/stats/nota-final/?&alumno={}&materia={}".format(
            self.alumno1.pk, self.materia.pk
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Es necesario especificar el id del anio_lectivo",
        )
