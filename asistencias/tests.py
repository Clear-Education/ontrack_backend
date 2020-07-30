from django.test import TestCase
from django.contrib.auth.models import Permission
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from users.models import User, Group
from instituciones.models import Institucion
from curricula.models import Carrera, AnioLectivo, Curso, Anio
from alumnos.models import Alumno, AlumnoCurso
from asistencias.models import Asistencia, AsistenciaAnioLectivo
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnList

# Create your tests here.
class AlumnoTests(APITestCase):
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
        cls.group_admin.save()

        cls.group_docente = Group.objects.create(name="Docente")
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Puede listar asistencias")
        )
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Can view asistencia")
        )
        cls.group_docente.save()

        cls.institucion_1 = Institucion.objects.create(nombre="Institucion_1")
        cls.institucion_1.save()
        cls.institucion_2 = Institucion.objects.create(nombre="Institucion_2")
        cls.institucion_2.save()

        cls.user_admin = User.objects.create_user(
            "admin@admin.com",
            password="password",
            groups=cls.group_admin,
            institucion=cls.institucion_1,
        )
        cls.user_docente = User.objects.create_user(
            "docente@docente.com",
            password="password",
            groups=cls.group_docente,
            institucion=cls.institucion_1,
        )

        cls.carrera_1 = Carrera.objects.create(
            nombre="Carrera1",
            descripcion=".",
            institucion=cls.institucion_1,
            color=".",
        )
        cls.carrera_1.save()

        cls.carrera_2 = Carrera.objects.create(
            nombre="Carrera2",
            descripcion=".",
            institucion=cls.institucion_2,
            color=".",
        )
        cls.carrera_2.save()

        cls.anio_1 = Anio.objects.create(
            nombre="Anio1", carrera=cls.carrera_1, color="."
        )
        cls.anio_1.save()

        cls.anio_2 = Anio.objects.create(
            nombre="Anio2", carrera=cls.carrera_2, color="."
        )
        cls.anio_2.save()

        cls.curso_1 = Curso.objects.create(nombre="Curso1", anio=cls.anio_1)
        cls.curso_1.save()

        cls.curso_2 = Curso.objects.create(nombre="Curso2", anio=cls.anio_1)
        cls.curso_2.save()

        cls.curso_3 = Curso.objects.create(nombre="Curso3", anio=cls.anio_2)
        cls.curso_3.save()

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

        cls.anio_lectivo_3 = AnioLectivo.objects.create(
            nombre="2021",
            fecha_desde="2021-01-01",
            fecha_hasta="2021-12-31",
            institucion=cls.institucion_2,
        )
        cls.anio_lectivo_3.save()

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

        cls.alumno_3 = Alumno.objects.create(
            dni=3,
            nombre="Alumno",
            apellido="3",
            institucion=cls.institucion_1,
        )
        cls.alumno_3.save()

        cls.alumno_curso_1 = AlumnoCurso.objects.create(
            alumno=cls.alumno_1,
            curso=cls.curso_1,
            anio_lectivo=cls.anio_lectivo_1,
        )
        cls.alumno_curso_1.save()

        cls.alumno_curso_2 = AlumnoCurso.objects.create(
            alumno=cls.alumno_1,
            curso=cls.curso_2,
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
            curso=cls.curso_2,
            anio_lectivo=cls.anio_lectivo_2,
        )
        cls.alumno_curso_4.save()

        cls.alumno_curso_5 = AlumnoCurso.objects.create(
            alumno=cls.alumno_2,
            curso=cls.curso_2,
            anio_lectivo=cls.anio_lectivo_1,
        )
        cls.alumno_curso_5.save()

        cls.alumno_curso_6 = AlumnoCurso.objects.create(
            alumno=cls.alumno_3,
            curso=cls.curso_3,
            anio_lectivo=cls.anio_lectivo_3,
        )
        cls.alumno_curso_6.save()

    def test_create_multiple_asistencias_admin(self):
        """
        Test de creacion correcta de Asistencias por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        data = [
            {
                "fecha": "01/11/2019",
                "asistio": 1,
                "alumno_curso": self.alumno_curso_1.id,
            },
            {
                "fecha": "01/11/2019",
                "asistio": 1,
                "alumno_curso": self.alumno_curso_3.id,
            },
        ]
        response = self.client.post(
            "/api/asistencias/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_multiple_asistencias_docente(self):
        """
        Test de creacion de Asistencias por docente
        """
        self.client.force_authenticate(user=self.user_docente)
        data = [
            {
                "fecha": "01/11/2019",
                "asistio": 1,
                "alumno_curso": self.alumno_curso_1.id,
            },
            {
                "fecha": "01/11/2019",
                "asistio": 1,
                "alumno_curso": self.alumno_curso_3.id,
            },
        ]
        response = self.client.post(
            "/api/asistencias/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_multiple_campos_faltantes(self):
        """
        Test de creacion de Asistencias con campos faltantes
        """
        self.client.force_authenticate(user=self.user_admin)
        data = [
            {
                "fecha": "01/11/2019",
                "asistio": 1,
                "alumno_curso": self.alumno_curso_1.id,
            },
            {"asistio": 1, "alumno_curso": self.alumno_curso_3.id,},
        ]
        response = self.client.post(
            "/api/asistencias/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[1].get("fecha")[0].code, "required")

    def test_create_multiple_sin_datos(self):
        """
        Test de creacion de Asistencias sin datos
        """
        self.client.force_authenticate(user=self.user_admin)
        data = []
        response = self.client.post(
            "/api/asistencias/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("detail"), "No se recibió ninguna información"
        )

    def test_create_multiple_distintos_cursos(self):
        """
        Test de creacion de Asistencias de distintos cursos
        """
        self.client.force_authenticate(user=self.user_admin)
        data = [
            {
                "fecha": "01/11/2019",
                "asistio": 1,
                "alumno_curso": self.alumno_curso_1.id,
            },
            {
                "fecha": "01/11/2019",
                "asistio": 1,
                "alumno_curso": self.alumno_curso_5.id,
            },
        ]
        response = self.client.post(
            "/api/asistencias/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("detail"),
            "No se pueden cargar asistencias para cursos distintos al mismo tiempo",
        )

