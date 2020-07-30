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
from django.urls import reverse
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnList


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
        cls.institucion = Institucion.objects.create(nombre="MIT")
        cls.institucion2 = Institucion.objects.create(nombre="SNU")

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

        cls.evaluacion1 = Evaluacion.objects.create(
            **{
                "anio_lectivo": cls.anio_lectivo,
                "materia": cls.materia,
                "ponderacion": 0.5,
            }
        )
        cls.evaluacion2 = Evaluacion.objects.create(
            **{
                "anio_lectivo": cls.anio_lectivo,
                "materia": cls.materia,
                "ponderacion": 0.3,
            }
        )
        cls.evaluacion3 = Evaluacion.objects.create(
            **{
                "anio_lectivo": cls.anio_lectivo,
                "materia": cls.materia,
                "ponderacion": 0.2,
            }
        )

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

    def test_create_multiples_calificaciones(self):
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

    def test_create_invalid_multiples_calificaciones(self):
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

    def test_create_single_calificaciones(self):
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

    def test_create_invalid_single_calificaciones(self):
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
