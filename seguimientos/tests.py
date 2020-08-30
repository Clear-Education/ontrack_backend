from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework.utils.serializer_helpers import ReturnList

from users.models import User, Group
from django.contrib.auth.models import Permission
from seguimientos.models import Seguimiento, RolSeguimiento
from instituciones.models import Institucion
from curricula.models import (
    Carrera,
    Anio,
    AnioLectivo,
    Evaluacion,
    Materia,
    Curso,
)
from alumnos.models import Alumno, AlumnoCurso
from django.urls import reverse
from rest_framework import status


class SeguimientosTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup de User y permisos para poder ejecutar todas las acciones
        """
        cls.client = APIClient()
        cls.group = Group.objects.create(name="Pedagogía")
        cls.group_docente = Group.objects.create(name="Docente")

        cls.group.permissions.add(
            *Permission.objects.values_list("id", flat=True)
        )
        cls.institucion = Institucion.objects.create(nombre="MIT")
        cls.user = User.objects.create_user(
            "juan@juan.com",
            password="juan123",
            groups=cls.group,
            institucion=cls.institucion,
        )
        cls.user_docente = User.objects.create_user(
            "juandocente@juan.com",
            password="juan123",
            groups=cls.group_docente,
            institucion=cls.institucion,
        )
        cls.rol_pedagogo = RolSeguimiento.objects.create(
            nombre="Encargado de Seguimiento"
        )
        cls.rol_profesor = RolSeguimiento.objects.create(nombre="Profesor")
        cls.rol_tutor = RolSeguimiento(nombre="Tutor")

        # Estructura curricular

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
                "fecha_desde": "2020-03-12",
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
            nombre="Alumno2",
            apellido="Alume2",
            institucion=cls.institucion,
        )
        cls.alumno_curso2 = AlumnoCurso.objects.create(
            alumno=cls.alumno2, curso=cls.curso, anio_lectivo=cls.anio_lectivo,
        )

    def setUp(self):
        """
            Fuerzo la autenticacion en cada corrida
        """
        self.client.force_authenticate(user=self.user)

    def test_create_seguimiento(self):
        """
        Test de creacion de seguimientos
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Seguimiento.objects.count(), 1)
        self.assertEqual(
            Seguimiento.objects.get().nombre, "Primer Seguimiento"
        )

    def test_create_seguimiento_con_integrantes(self):
        """
        Test de creacion de seguimientos + integrantes
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
                {"usuario": self.user_docente.pk, "rol": self.rol_profesor.pk},
            ],
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Seguimiento.objects.count(), 1)
        self.assertEqual(
            Seguimiento.objects.get().nombre, "Primer Seguimiento"
        )

    def test_create_seguimiento_con_integrantes_invalid(self):
        """
        Test de creacion de seguimientos + integrantes con roles malos
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
                {"usuario": self.user_docente.pk, "rol": self.rol_pedagogo.pk},
            ],
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Seguimiento.objects.count(), 0)

    def test_create_seguimiento_con_materias(self):
        """
        Test de creacion de seguimientos + materias
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "materias": [self.materia.pk,],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Seguimiento.objects.count(), 1)
        self.assertEqual(
            Seguimiento.objects.get().nombre, "Primer Seguimiento"
        )

    def test_create_seguimiento_con_materias_invalid(self):
        """
        Test de creacion de seguimientos + materias
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "materias": 9,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Seguimiento.objects.count(), 0)
