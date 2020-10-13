from django.test import TestCase
import datetime
from django.contrib.auth.models import Permission
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from users.models import User, Group
from instituciones.models import Institucion
from curricula.models import Carrera, AnioLectivo, Curso, Anio, Materia
from alumnos.models import Alumno, AlumnoCurso
from seguimientos.models import (
    Seguimiento,
    IntegranteSeguimiento,
    RolSeguimiento,
)
from rest_framework import status


class ObjetivoTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup de User y permisos para poder ejecutar todas las acciones
        """
        cls.client = APIClient()
        cls.group_admin = Group.objects.create(name="Admin")
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can add actualizacion")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can change actualizacion")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can delete actualizacion")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Puede listar actualizaciones")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can view actualizacion")
        )
        cls.group_admin.save()

        cls.institucion_1 = Institucion.objects.create(
            nombre="Institucion_1", identificador="1234"
        )

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
            nombre="2020",
            fecha_desde="2020-01-01",
            fecha_hasta="2020-12-31",
            institucion=cls.institucion_1,
        )

        cls.alumno_1 = Alumno.objects.create(
            dni=1,
            nombre="Alumno",
            apellido="1",
            institucion=cls.institucion_1,
        )

        cls.alumno_curso_1 = AlumnoCurso.objects.create(
            alumno=cls.alumno_1,
            curso=cls.curso_1,
            anio_lectivo=cls.anio_lectivo_1,
        )

        cls.materia_1 = Materia.objects.create(
            nombre="Matematicas", anio=cls.anio_1
        )

        cls.seguimiento_1 = Seguimiento.objects.create(
            nombre="seguimiento_1",
            en_progreso=True,
            institucion=cls.institucion_1,
            fecha_inicio=datetime.date(2020, 1, 1),
            fecha_cierre=datetime.date(2020, 12, 31),
            descripcion=".",
            anio_lectivo=cls.anio_lectivo_1,
        )
        cls.seguimiento_1.alumnos.add(cls.alumno_curso_1)
        cls.seguimiento_1.materias.add(cls.materia_1)
        cls.seguimiento_1.save()

        cls.rol_1 = RolSeguimiento.objects.create(
            nombre="Encargado de Seguimiento"
        )

        cls.rol_2 = RolSeguimiento.objects.create(nombre="Otro")

        cls.integrante_1 = IntegranteSeguimiento.objects.create(
            seguimiento=cls.seguimiento_1,
            usuario=cls.user_admin,
            rol=cls.rol_1,
            fecha_desde=datetime.date(2020, 1, 1),
        )

    #############
    #   CREATE  #
    #############
    def test_create_actualizacion(self):
        """
        Test de creacion correcta de Actualizacion
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento = self.seguimiento_1.id
        data = {
            "cuerpo": "cuerpo de actualizacion",
        }
        response = self.client.post(
            f"/api/actualizaciones/{seguimiento}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(f"/api/actualizaciones/{seguimiento}/list/")
        self.assertEqual(response.data["count"], 1)

        data = {
            "cuerpo": "cuerpo del comentario",
            "padre": response.data["results"][0]["id"],
        }
        response2 = self.client.post(
            f"/api/actualizaciones/{seguimiento}/", data, format="json"
        )
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        response3 = self.client.get(
            f"/api/actualizaciones/{seguimiento}/list/"
        )
        self.assertEqual(len(response3.data["results"][0]["comentarios"]), 1)

        response4 = self.client.delete(
            f"/api/actualizaciones/{response.data['results'][0]['id']}/mix/",
        )
        self.assertEqual(response4.status_code, status.HTTP_200_OK)

        response = self.client.get(f"/api/actualizaciones/{seguimiento}/list/")
        self.assertEqual(response.data["count"], 0)
