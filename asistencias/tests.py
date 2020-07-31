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
            institucion=cls.institucion_2,
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

        cls.asistencia_1 = Asistencia.objects.create(
            fecha="2019-11-15",
            asistio=1,
            descripcion="Hola",
            alumno_curso=cls.alumno_curso_1,
        )
        cls.asistencia_1.save()

        cls.asistencia_2 = Asistencia.objects.create(
            fecha="2019-11-22", asistio=0, alumno_curso=cls.alumno_curso_1,
        )
        cls.asistencia_2.save()

        cls.asistencia_3 = Asistencia.objects.create(
            fecha="2019-11-22", asistio=1, alumno_curso=cls.alumno_curso_3,
        )
        cls.asistencia_3.save()

        cls.asistencia_4 = Asistencia.objects.create(
            fecha="2021-01-05",
            asistio=1,
            descripcion="Otra inst",
            alumno_curso=cls.alumno_curso_6,
        )
        cls.asistencia_4.save()

    #############
    #  CREATE + #
    #############

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

    def test_create_multiple_asistencias_de_otra_institucion(self):
        """
        Test de creacion de Asistencias de otra institucion
        """
        self.client.force_authenticate(user=self.user_admin)
        data = [
            {
                "fecha": "01/11/2019",
                "asistio": 1,
                "alumno_curso": self.alumno_curso_6.id,
            },
        ]
        response = self.client.post(
            "/api/asistencias/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get("detail"), "No encontrado.",
        )

    def test_create_multiple_asistencias_no_existente(self):
        """
        Test de creacion de Asistencias no existente
        """
        self.client.force_authenticate(user=self.user_admin)
        data = [
            {
                "fecha": "01/11/2019",
                "asistio": 1,
                "alumno_curso": self.alumno_curso_1.id,
            },
            {"fecha": "01/11/2019", "asistio": 1, "alumno_curso": 250,},
        ]
        response = self.client.post(
            "/api/asistencias/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get("detail"), "No encontrado.",
        )

    def test_create_multiple_asistencias_rango_incorrecto(self):
        """
        Test de creacion de Asistencias con asistio en rango incorrecto
        """
        self.client.force_authenticate(user=self.user_admin)
        data = [
            {
                "fecha": "01/11/2019",
                "asistio": 0,
                "alumno_curso": self.alumno_curso_1.id,
            },
            {
                "fecha": "01/11/2019",
                "asistio": -1,
                "alumno_curso": self.alumno_curso_3.id,
            },
        ]
        response = self.client.post(
            "/api/asistencias/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data[1].get("asistio")[0]),
            "El valor del campo asistencia solo puede estar entre 0 y 1",
        )

    def test_create_multiple_asistencias_distintas_fechas(self):
        """
        Test de creacion de Asistencias con distintas fechas
        """
        self.client.force_authenticate(user=self.user_admin)
        data = [
            {
                "fecha": "01/11/2019",
                "asistio": 0,
                "alumno_curso": self.alumno_curso_1.id,
            },
            {
                "fecha": "08/11/2019",
                "asistio": 1,
                "alumno_curso": self.alumno_curso_3.id,
            },
        ]
        response = self.client.post(
            "/api/asistencias/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("detail"),
            "No se pueden cargar asistencias para distintas fechas al mismo tiempo",
        )

    def test_create_multiple_asistencias_alumno_curso_repetido(self):
        """
        Test de creacion de Asistencias con alumno_curso repetido
        """
        self.client.force_authenticate(user=self.user_admin)
        data = [
            {
                "fecha": "01/11/2019",
                "asistio": 0,
                "alumno_curso": self.alumno_curso_1.id,
            },
            {
                "fecha": "01/11/2019",
                "asistio": 1,
                "alumno_curso": self.alumno_curso_1.id,
            },
        ]
        response = self.client.post(
            "/api/asistencias/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("detail"),
            "No se pueden repetir alumnos en una misma llamada",
        )

    def test_create_multiple_asistencias_fecha_fuera_rango(self):
        """
        Test de creacion de Asistencias con fecha fuera de rango
        """
        self.client.force_authenticate(user=self.user_admin)
        data = [
            {
                "fecha": "30/07/2020",
                "asistio": 0,
                "alumno_curso": self.alumno_curso_1.id,
            },
            {
                "fecha": "30/07/2020",
                "asistio": 1,
                "alumno_curso": self.alumno_curso_3.id,
            },
        ]
        response = self.client.post(
            "/api/asistencias/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("detail"),
            "La fecha especificada no se encuentra dentro del Año Lectivo",
        )

    def test_create_multiple_asistencias_fecha_fin_de_semana(self):
        """
        Test de creacion de Asistencias con fecha fin de semana
        """
        self.client.force_authenticate(user=self.user_admin)
        data = [
            {
                "fecha": "02/11/2019",
                "asistio": 0,
                "alumno_curso": self.alumno_curso_1.id,
            },
            {
                "fecha": "02/11/2019",
                "asistio": 1,
                "alumno_curso": self.alumno_curso_3.id,
            },
        ]
        response = self.client.post(
            "/api/asistencias/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("detail"),
            "No se pueden cargar asistencias para fines de semana",
        )

    def test_create_multiple_asistencias_ya_existente(self):
        """
        Test de creacion de Asistencias con asistencia ya existente
        """
        self.client.force_authenticate(user=self.user_admin)
        data = [
            {
                "fecha": "01/11/2019",
                "asistio": 0,
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
        response = self.client.post(
            "/api/asistencias/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("detail"),
            "Ya existen asistencias cargadas para algun alumno de los listados en el día especificado. Se debe modificar o borrar dicha asistencia",
        )

    #############
    #   CREATE  #
    #############

    def test_create_asistencia_admin(self):
        """
        Test de creacion correcta de Asistencia por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        data = {
            "fecha": "01/11/2019",
            "asistio": 1,
            "alumno_curso": self.alumno_curso_1.id,
        }
        response = self.client.post("/api/asistencias/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_asistencia_docente(self):
        """
        Test de creacion de Asistencia por docente
        """
        self.client.force_authenticate(user=self.user_docente)
        data = {
            "fecha": "01/11/2019",
            "asistio": 1,
            "alumno_curso": self.alumno_curso_1.id,
        }
        response = self.client.post("/api/asistencias/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_campos_faltantes(self):
        """
        Test de creacion de Asistencia con campos faltantes
        """
        self.client.force_authenticate(user=self.user_admin)
        data = {
            "asistio": 1,
            "alumno_curso": self.alumno_curso_3.id,
        }

        response = self.client.post("/api/asistencias/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("fecha")[0].code, "required")

    def test_create_asistencia_de_otra_institucion(self):
        """
        Test de creacion de Asistencia de otra institucion
        """
        self.client.force_authenticate(user=self.user_admin)
        data = {
            "fecha": "01/11/2019",
            "asistio": 1,
            "alumno_curso": self.alumno_curso_6.id,
        }
        response = self.client.post("/api/asistencias/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get("detail"), "No encontrado.",
        )

    def test_create_asistencia_no_existente(self):
        """
        Test de creacion de Asistencia no existente
        """
        self.client.force_authenticate(user=self.user_admin)
        data = {
            "fecha": "01/11/2019",
            "asistio": 1,
            "alumno_curso": 250,
        }

        response = self.client.post("/api/asistencias/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get("detail"), "No encontrado.",
        )

    def test_create_asistencia_rango_incorrecto(self):
        """
        Test de creacion de Asistencia con asistio en rango incorrecto
        """
        self.client.force_authenticate(user=self.user_admin)
        data = {
            "fecha": "01/11/2019",
            "asistio": -1,
            "alumno_curso": self.alumno_curso_3.id,
        }
        response = self.client.post("/api/asistencias/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data.get("asistio")[0]),
            "El valor del campo asistencia solo puede estar entre 0 y 1",
        )

    def test_create_asistencia_fecha_fuera_rango(self):
        """
        Test de creacion de Asistencia con fecha fuera de rango
        """
        self.client.force_authenticate(user=self.user_admin)
        data = {
            "fecha": "30/07/2020",
            "asistio": 0,
            "alumno_curso": self.alumno_curso_1.id,
        }
        response = self.client.post("/api/asistencias/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("detail"),
            "La fecha especificada no se encuentra dentro del Año Lectivo",
        )

    def test_create_asistencia_fecha_fin_de_semana(self):
        """
        Test de creacion de Asistencia con fecha fin de semana
        """
        self.client.force_authenticate(user=self.user_admin)
        data = {
            "fecha": "02/11/2019",
            "asistio": 0,
            "alumno_curso": self.alumno_curso_1.id,
        }
        response = self.client.post("/api/asistencias/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("detail"),
            "No se pueden cargar asistencias para fines de semana",
        )

    def test_create_asistencia_ya_existente(self):
        """
        Test de creacion de Asistencia con asistencia ya existente
        """
        self.client.force_authenticate(user=self.user_admin)
        data = {
            "fecha": "01/11/2019",
            "asistio": 0,
            "alumno_curso": self.alumno_curso_1.id,
        }
        response = self.client.post("/api/asistencias/", data, format="json")
        response = self.client.post("/api/asistencias/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("detail"),
            "Ya existen una asistencia cargada para el alumno en el día especificado. Se debe modificar o borrar dicha asistencia",
        )

    #############
    #    GET    #
    #############

    def test_get_asistencia_admin(self):
        """
        Test de obtención de Asistencia por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.get(f"/api/asistencias/{self.asistencia_1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("id"), self.asistencia_1.id)

    def test_get_asistencia_docente(self):
        """
        Test de obtención de Asistencia por docente
        """
        self.client.force_authenticate(user=self.user_docente)
        response = self.client.get(f"/api/asistencias/{self.asistencia_1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("id"), self.asistencia_1.id)

    def test_get_asistencia_otra_institucion(self):
        """
        Test de obtención de Asistencia de otra institucion
        """
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.get(f"/api/asistencias/{self.asistencia_4.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_asistencia_no_existente(self):
        """
        Test de obtención de Asistencia no existente
        """
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.get("/api/asistencias/265/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    #############
    #   UPDATE  #
    #############

    def test_update_asistencia_admin(self):
        """
        Test de modificacion de Asistencia por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        data = {
            "asistio": 1,
            "descripcion": "cambiado",
        }
        response = self.client.patch(
            f"/api/asistencias/{self.asistencia_1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_asistencia_docente(self):
        """
        Test de modificacion de Asistencia por docente
        """
        self.client.force_authenticate(user=self.user_docente)
        data = {
            "asistio": 1,
            "descripcion": "cambiado",
        }
        response = self.client.patch(
            f"/api/asistencias/{self.asistencia_1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_asistencia_otra_institucion(self):
        """
        Test de modificacion de Asistencia de otra institucion
        """
        self.client.force_authenticate(user=self.user_admin)
        data = {
            "asistio": 1,
            "descripcion": "cambiado",
        }
        response = self.client.patch(
            f"/api/asistencias/{self.asistencia_4.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_asistencia_no_existente(self):
        """
        Test de modificacion de Asistencia no existente
        """
        self.client.force_authenticate(user=self.user_admin)
        data = {
            "asistio": 1,
            "descripcion": "cambiado",
        }
        response = self.client.patch(
            "/api/asistencias/500/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_asistencia_vacio(self):
        """
        Test de modificacion de Asistencia no existente
        """
        self.client.force_authenticate(user=self.user_admin)
        data = {}
        response = self.client.patch(
            f"/api/asistencias/{self.asistencia_1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Body vacío.")

