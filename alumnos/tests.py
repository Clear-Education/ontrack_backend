from django.test import TestCase
from django.contrib.auth.models import Permission
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from users.models import User, Group
from instituciones.models import Institucion
from curricula.models import Carrera, AnioLectivo, Curso, Anio
from alumnos.models import Alumno, AlumnoCurso
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnList


class AlumnoTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup de User y permisos para poder ejecutar todas las acciones
        """
        cls.client = APIClient()
        cls.group_admin = Group.objects.create(name="Admin")
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can add alumno")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can change alumno")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can delete alumno")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Puede listar alumnos")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can view alumno")
        )
        cls.group_admin.save()

        cls.group_docente = Group.objects.create(name="Docente")
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Puede listar alumnos")
        )
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Can view alumno")
        )
        cls.group_docente.save()

        cls.institucion_1 = Institucion.objects.create(
            nombre="Institucion_1", cuit=1
        )
        cls.institucion_2 = Institucion.objects.create(
            nombre="Institucion_2", cuit=2
        )

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

        cls.anio_1 = Anio.objects.create(
            nombre="Anio1", carrera=cls.carrera_1, color="."
        )

        cls.curso_1 = Curso.objects.create(nombre="CURSO1", anio=cls.anio_1)

        cls.anio_lectivo_1 = AnioLectivo.objects.create(
            nombre="2019",
            fecha_desde="2019-01-01",
            fecha_hasta="2020-12-31",
            institucion=cls.institucion_1,
        )

        cls.anio_lectivo_2 = AnioLectivo.objects.create(
            nombre="2020",
            fecha_desde="2019-01-01",
            fecha_hasta="2019-12-31",
            institucion=cls.institucion_2,
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

        cls.alumno_2 = Alumno.objects.create(
            dni=2,
            nombre="Alumno",
            apellido="2",
            institucion=cls.institucion_1,
        )

        cls.alumno_3 = Alumno.objects.create(
            dni=3,
            nombre="Alumno",
            apellido="3",
            institucion=cls.institucion_1,
        )

        cls.alumno_4 = Alumno.objects.create(
            dni=4,
            nombre="Alumno",
            apellido="4",
            institucion=cls.institucion_1,
        )

        cls.alumno_5 = Alumno.objects.create(
            dni=5,
            nombre="Alumno",
            apellido="5",
            institucion=cls.institucion_2,
        )

    def test_create_alumno_admin(self):
        """
        Test de creacion correcta de Alumno por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        data = [
            {
                "dni": 6,
                "nombre": "Danilo",
                "apellido": "Reitano",
                "email": "danilo@danilo.com.ar",
                "legajo": 1,
                "fecha_nacimiento": "08/02/1998",
                "direccion": "Calle",
                "localidad": "Departamento",
                "provincia": "Mendoza",
                "fecha_inscripcion": "01/01/2019",
                "institucion": 1,
            },
            {
                "dni": 7,
                "nombre": "Danilos",
                "apellido": "Reitanos",
                "institucion": 2,
            },
        ]
        response = self.client.post("/api/alumnos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_alumno_docente(self):
        """
        Test de creacion de Alumno por docente
        """
        self.client.force_authenticate(user=self.user_docente)
        data = [
            {
                "dni": 6,
                "nombre": "Danilo",
                "apellido": "Reitano",
                "email": "danilo@danilo.com.ar",
                "legajo": 1,
                "fecha_nacimiento": "08/02/1998",
                "direccion": "Calle",
                "localidad": "Departamento",
                "provincia": "Mendoza",
                "fecha_inscripcion": "01/01/2019",
                "institucion": 1,
            },
            {
                "dni": 7,
                "nombre": "Danilos",
                "apellido": "Reitanos",
                "institucion": 2,
            },
        ]
        response = self.client.post("/api/alumnos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_alumno_conflictivo(self):
        """
        Test de creación de Alumnos con conflictos
        """
        self.client.force_authenticate(user=self.user_admin)
        data = [
            {
                "dni": 10,
                "nombre": "Danilo",
                "apellido": "Reitano",
                "email": "danilo@danilo.com.ar",
                "legajo": 1,
                "fecha_nacimiento": "08/02/1998",
                "direccion": "Calle",
                "localidad": "Departamento",
                "provincia": "Mendoza",
                "fecha_inscripcion": "01/01/2019",
                "institucion": 1,
            },
            {
                "dni": 10,
                "nombre": "Danilos",
                "apellido": "Reitanos",
                "institucion": 2,
            },
        ]
        response = self.client.post("/api/alumnos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"], "Alumnos con el mismo dni en conflicto"
        )

        data = [
            {
                "dni": 1,
                "nombre": "Danilo",
                "apellido": "Reitano",
                "email": "danilo@danilo.com.ar",
                "legajo": 1,
                "fecha_nacimiento": "08/02/1998",
                "direccion": "Calle",
                "localidad": "Departamento",
                "provincia": "Mendoza",
                "fecha_inscripcion": "01/01/2019",
                "institucion": 1,
            },
        ]
        response = self.client.post("/api/alumnos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"], "Alumno con el mismo dni existente"
        )

    def test_update_alumno_admin(self):
        """
        Test de modificación correcta de Alumno por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        id_alumno = Alumno.objects.get(dni=1).id
        data = {
            "dni": 1,
            "nombre": "Danilor",
            "apellido": "Reitano",
            "email": "danilos@danilo.com.ar",
            "legajo": 1,
            "fecha_nacimiento": "08/02/1998",
            "direccion": "Calle",
            "localidad": "Departamento",
            "provincia": "Mendoza",
            "fecha_inscripcion": "01/01/2019",
        }
        response = self.client.patch(
            f"/api/alumnos/{id_alumno}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_alumno_docente(self):
        """
        Test de modificación de Alumno por docente
        """
        self.client.force_authenticate(user=self.user_docente)
        id_alumno = Alumno.objects.get(dni=1).id
        data = {
            "nombre": "Danilortgh",
            "direccion": "Calle",
            "localidad": "Departamento",
        }
        response = self.client.patch(
            f"/api/alumnos/{id_alumno}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_alumno_admin_no_existente_o_distinta_institucion(self):
        """
        Test de modificación de Alumno no existente o de otra institucion por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        id_alumno = Alumno.objects.get(dni=5).id
        data = {
            "localidad": "Departamento",
        }
        response = self.client.patch(
            f"/api/alumnos/{id_alumno}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.patch(f"/api/alumnos/200/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_alumno_admin_info_conflictiva(self):
        """
        Test de modificación correcta de Alumno por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        id_alumno = Alumno.objects.get(dni=1).id
        data = {
            "dni": 5,
            "nombre": "Danilor",
            "apellido": "Reitano",
        }
        response = self.client.patch(
            f"/api/alumnos/{id_alumno}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_alumno_admin(self):
        """
        Test de obtencion correcta de Alumno por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        id_alumno = Alumno.objects.get(dni=1).id
        response = self.client.get(f"/api/alumnos/{id_alumno}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_alumno_docente(self):
        """
        Test de obtencion correcta de Alumno por docente
        """
        self.client.force_authenticate(user=self.user_docente)
        id_alumno = Alumno.objects.get(dni=1).id
        response = self.client.get(f"/api/alumnos/{id_alumno}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_alumno_admin_no_existente_o_distinta_institucion(self):
        """
        Test de obtencion de Alumno no existente o de distinta institucion por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        id_alumno = Alumno.objects.get(dni=5).id
        response = self.client.get(f"/api/alumnos/{id_alumno}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get("/api/alumnos/40/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_alumno_admin(self):
        """
        Test de listado de Alumno por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.get("/api/alumnos/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 4)

    def test_list_alumno_docente(self):
        """
        Test de listado de Alumno por docente
        """
        self.client.force_authenticate(user=self.user_docente)
        response = self.client.get("/api/alumnos/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 4)

    def test_list_alumno_con_query_param(self):
        """
        Test de listado correcto de Alumno con query param
        """
        self.client.force_authenticate(user=self.user_admin)
        anio_lectivo = self.anio_lectivo_1.id

        response = self.client.get(
            f"/api/alumnos/list/?anio_lectivo={anio_lectivo}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_list_alumno_con_anio_lectivo_no_numerico(self):
        """
        Test de listado de Alumno con anio_lectivo no numerico
        """
        self.client.force_authenticate(user=self.user_admin)

        response = self.client.get(f"/api/alumnos/list/?anio_lectivo=x")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"], "El valor de Año Lectivo no es numérico"
        )

    def test_list_alumno_con_anio_lectivo_no_existente(self):
        """
        Test de listado de Alumno con anio_lectivo no existente
        """
        self.client.force_authenticate(user=self.user_admin)

        response = self.client.get(f"/api/alumnos/list/?anio_lectivo=2000")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

    def test_list_alumno_con_alumno_curso_otra_institucion(self):
        """
        Test de listado de Alumno con anio_lectivo de otra institucion
        """
        self.client.force_authenticate(user=self.user_admin)
        anio_lectivo = self.anio_lectivo_2.id

        response = self.client.get(
            f"/api/alumnos/list/?anio_lectivo={anio_lectivo}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

    def test_delete_alumno_admin(self):
        """
        Test de borrado de Alumno correcto por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        id_alumno = self.alumno_2.pk
        response = self.client.delete(f"/api/alumnos/{id_alumno}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_alumno_admin_while_active(self):
        """
        Test de borrado de Alumno incorrecto por admin
        """
        self.client.force_authenticate(user=self.user_admin)

        id_alumno = self.alumno_curso_1.alumno.pk
        response = self.client.delete(f"/api/alumnos/{id_alumno}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_alumno_admin_no_existente_o_distinta_institucion(self):
        """
        Test de borrado de Alumno no existente o de distinta institucion por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        id_alumno = Alumno.objects.get(dni=5).id
        response = self.client.delete(f"/api/alumnos/{id_alumno}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete("/api/alumnos/45/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_alumno_docente(self):
        """
        Test de borrado de Alumno por docente
        """
        self.client.force_authenticate(user=self.user_docente)
        id_alumno = Alumno.objects.get(dni=2).id
        response = self.client.delete(f"/api/alumnos/{id_alumno}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AlumnoCursoTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup de User y permisos para poder ejecutar todas las acciones
        """
        cls.client = APIClient()
        cls.group_admin = Group.objects.create(name="Admin")
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can add alumno")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can change alumno")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can delete alumno")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Puede listar alumnos")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Puede crear multiples alumnocurso")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can view alumno")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can add alumno curso")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can change alumno curso")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can delete alumno curso")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Puede listar alumnocurso")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can view alumno curso")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Puede borrar multiples alumnocurso")
        )
        cls.group_admin.save()

        cls.group_docente = Group.objects.create(name="Docente")
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Puede listar alumnos")
        )
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Can view alumno")
        )
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Can view alumno curso")
        )
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Puede listar alumnocurso")
        )
        cls.group_docente.save()

        cls.institucion_1 = Institucion.objects.create(
            nombre="Institucion_1", cuit=1
        )
        cls.institucion_1.save()
        cls.institucion_2 = Institucion.objects.create(
            nombre="Institucion_2", cuit=2
        )
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

        cls.curso_1 = Curso.objects.create(nombre="CURSO1", anio=cls.anio_1)
        cls.curso_1.save()

        cls.curso_2 = Curso.objects.create(nombre="CURSO2", anio=cls.anio_1)
        cls.curso_2.save()

        cls.curso_3 = Curso.objects.create(nombre="CURSO3", anio=cls.anio_2)
        cls.curso_3.save()

        cls.curso_4 = Curso.objects.create(nombre="CURSO4", anio=cls.anio_1)

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

        cls.anio_lectivo_4 = AnioLectivo.objects.create(
            nombre="2022",
            fecha_desde="2022-01-01",
            fecha_hasta="2022-12-31",
            institucion=cls.institucion_1,
        )

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

        cls.alumno_4 = Alumno.objects.create(
            dni=4,
            nombre="Alumno",
            apellido="4",
            institucion=cls.institucion_1,
        )
        cls.alumno_4.save()

        cls.alumno_5 = Alumno.objects.create(
            dni=5,
            nombre="Alumno",
            apellido="5",
            institucion=cls.institucion_2,
        )
        cls.alumno_5.save()

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
            alumno=cls.alumno_3,
            curso=cls.curso_1,
            anio_lectivo=cls.anio_lectivo_2,
        )
        cls.alumno_curso_5.save()

        cls.alumno_curso_6 = AlumnoCurso.objects.create(
            alumno=cls.alumno_4,
            curso=cls.curso_2,
            anio_lectivo=cls.anio_lectivo_1,
        )
        cls.alumno_curso_6.save()

        cls.alumno_curso_7 = AlumnoCurso.objects.create(
            alumno=cls.alumno_5,
            curso=cls.curso_3,
            anio_lectivo=cls.anio_lectivo_3,
        )
        cls.alumno_curso_7.save()

    def test_delete_multiple_alumno_curso_admin(self):
        """
        Test de borrado multiple de AlumnoCurso por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        alumno_1 = Alumno.objects.get(apellido="1").pk
        curso_1 = Curso.objects.get(nombre="CURSO1").pk
        anio_lectivo_1 = AnioLectivo.objects.get(nombre="2019").pk
        alumno_2 = Alumno.objects.get(apellido="5").pk
        curso_2 = Curso.objects.get(nombre="CURSO3").pk
        anio_lectivo_2 = AnioLectivo.objects.get(nombre="2021").pk
        data = [
            {
                "alumno": alumno_1,
                "curso": curso_1,
                "anio_lectivo": anio_lectivo_1,
            },
            {
                "alumno": alumno_2,
                "curso": curso_2,
                "anio_lectivo": anio_lectivo_2,
            },
        ]
        response = self.client.delete(
            "/api/alumnos/curso/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(AlumnoCurso.objects.all()), 6)

    def test_create_multiple_alumno_curso_admin(self):
        """
        Test de creacion multiple de AlumnoCurso por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        alumno_1 = Alumno.objects.get(apellido="1").pk
        alumno_2 = Alumno.objects.get(apellido="2").pk
        curso = Curso.objects.get(nombre="CURSO2").pk
        anio_lectivo = AnioLectivo.objects.get(nombre="2022").pk
        data = [
            {
                "alumno": alumno_1,
                "curso": curso,
                "anio_lectivo": anio_lectivo,
            },
            {
                "alumno": alumno_2,
                "curso": curso,
                "anio_lectivo": anio_lectivo,
            },
        ]
        response = self.client.post(
            "/api/alumnos/curso/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_multiple_alumno_curso_docente(self):
        """
        Test de creacion multiple de AlumnoCurso por docente
        """
        self.client.force_authenticate(user=self.user_docente)
        alumno_1 = Alumno.objects.get(apellido="1").pk
        alumno_2 = Alumno.objects.get(apellido="2").pk
        curso = Curso.objects.get(nombre="CURSO2").pk
        anio_lectivo = AnioLectivo.objects.get(nombre="2022").pk
        data = [
            {
                "alumno": alumno_1,
                "curso": curso,
                "anio_lectivo": anio_lectivo,
            },
            {
                "alumno": alumno_2,
                "curso": curso,
                "anio_lectivo": anio_lectivo,
            },
        ]
        response = self.client.post(
            "/api/alumnos/curso/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_multiple_alumno_curso_vacio(self):
        """
        Test de creacion multiple de AlumnoCurso vacio
        """
        self.client.force_authenticate(user=self.user_admin)
        data = []
        response = self.client.post(
            "/api/alumnos/curso/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"], "No se recibió ninguna información"
        )

    def test_create_multiple_alumno_curso_not_existing(self):
        """
        Test de creacion multiple de AlumnoCurso no existente
        """
        self.client.force_authenticate(user=self.user_admin)
        alumno_1 = Alumno.objects.get(apellido="1").pk
        alumno_2 = Alumno.objects.get(apellido="2").pk
        curso = Curso.objects.get(nombre="CURSO2").pk
        anio_lectivo = AnioLectivo.objects.get(nombre="2022").pk
        data = [
            {"alumno": 400, "curso": curso, "anio_lectivo": anio_lectivo,},
            {
                "alumno": alumno_2,
                "curso": curso,
                "anio_lectivo": anio_lectivo,
            },
        ]
        response = self.client.post(
            "/api/alumnos/curso/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

        data = [
            {
                "alumno": alumno_1,
                "curso": curso,
                "anio_lectivo": anio_lectivo,
            },
            {"alumno": alumno_2, "curso": 5000, "anio_lectivo": anio_lectivo,},
        ]
        response = self.client.post(
            "/api/alumnos/curso/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

        data = [
            {
                "alumno": alumno_1,
                "curso": curso,
                "anio_lectivo": anio_lectivo,
            },
            {"alumno": alumno_2, "curso": curso, "anio_lectivo": 5000,},
        ]
        response = self.client.post(
            "/api/alumnos/curso/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

    def test_create_multiple_alumno_curso_distintos(self):
        """
        Test de creacion multiple de AlumnoCurso distintos
        """
        self.client.force_authenticate(user=self.user_admin)
        alumno_1 = Alumno.objects.get(apellido="1").pk
        alumno_2 = Alumno.objects.get(apellido="2").pk
        curso_1 = Curso.objects.get(nombre="CURSO2").pk
        curso_2 = Curso.objects.get(nombre="CURSO1").pk
        anio_lectivo_1 = AnioLectivo.objects.get(nombre="2022").pk
        anio_lectivo_2 = AnioLectivo.objects.get(nombre="2019").pk
        data = [
            {
                "alumno": alumno_1,
                "curso": curso_1,
                "anio_lectivo": anio_lectivo_1,
            },
            {
                "alumno": alumno_2,
                "curso": curso_2,
                "anio_lectivo": anio_lectivo_1,
            },
        ]
        response = self.client.post(
            "/api/alumnos/curso/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "No se puede asignar a distintos cursos en una misma llamada",
        )

        data = [
            {
                "alumno": alumno_1,
                "curso": curso_1,
                "anio_lectivo": anio_lectivo_1,
            },
            {
                "alumno": alumno_2,
                "curso": curso_1,
                "anio_lectivo": anio_lectivo_2,
            },
        ]
        response = self.client.post(
            "/api/alumnos/curso/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "No se puede asignar a distintos Años Lectivos en una misma llamada",
        )

    def test_create_multiple_alumno_curso_repetido(self):
        """
        Test de creacion multiple de AlumnoCurso repetido
        """
        self.client.force_authenticate(user=self.user_admin)
        alumno_1 = Alumno.objects.get(apellido="1").pk
        alumno_2 = Alumno.objects.get(apellido="2").pk
        curso = Curso.objects.get(nombre="CURSO2").pk
        anio_lectivo = AnioLectivo.objects.get(nombre="2022").pk
        data = [
            {
                "alumno": alumno_1,
                "curso": curso,
                "anio_lectivo": anio_lectivo,
            },
            {
                "alumno": alumno_1,
                "curso": curso,
                "anio_lectivo": anio_lectivo,
            },
        ]
        response = self.client.post(
            "/api/alumnos/curso/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "No se puede asignar más de una vez a un Alumno en una misma llamada",
        )

    def test_create_multiple_alumno_curso_instituciones_distintas(self):
        """
        Test de creacion multiple de AlumnoCurso instituciones distintas
        """
        self.client.force_authenticate(user=self.user_admin)
        alumno_1 = Alumno.objects.get(apellido="1").pk
        alumno_2 = Alumno.objects.get(apellido="5").pk
        curso = Curso.objects.get(nombre="CURSO2").pk
        anio_lectivo = AnioLectivo.objects.get(nombre="2022").pk
        data = [
            {
                "alumno": alumno_1,
                "curso": curso,
                "anio_lectivo": anio_lectivo,
            },
            {
                "alumno": alumno_2,
                "curso": curso,
                "anio_lectivo": anio_lectivo,
            },
        ]
        response = self.client.post(
            "/api/alumnos/curso/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

    def test_create_multiple_alumno_curso_instituciones_distinta_con_curso_anio_lectivo(
        self,
    ):
        """
        Test de creacion multiple de AlumnoCurso instituciones distinas curso y anio lectivo
        """
        self.client.force_authenticate(user=self.user_admin)
        alumno_1 = Alumno.objects.get(apellido="1").pk
        alumno_2 = Alumno.objects.get(apellido="5").pk
        curso_1 = Curso.objects.get(nombre="CURSO2").pk
        curso_2 = Curso.objects.get(nombre="CURSO3").pk
        anio_lectivo_1 = AnioLectivo.objects.get(nombre="2022").pk
        anio_lectivo_2 = AnioLectivo.objects.get(nombre="2021").pk
        data = [
            {
                "alumno": alumno_1,
                "curso": curso_1,
                "anio_lectivo": anio_lectivo_2,
            }
        ]
        response = self.client.post(
            "/api/alumnos/curso/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

        data = [
            {
                "alumno": alumno_1,
                "curso": curso_2,
                "anio_lectivo": anio_lectivo_1,
            }
        ]
        response = self.client.post(
            "/api/alumnos/curso/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

        data = [
            {
                "alumno": alumno_2,
                "curso": curso_1,
                "anio_lectivo": anio_lectivo_1,
            }
        ]
        response = self.client.post(
            "/api/alumnos/curso/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

    def test_create_multiple_alumno_curso_distintos_cursos_un_anio(self):
        """
        Test de creacion multiple de AlumnoCurso multiples cursos en un año
        """
        self.client.force_authenticate(user=self.user_admin)
        alumno_1 = Alumno.objects.get(apellido="3").pk
        alumno_2 = Alumno.objects.get(apellido="4").pk
        curso = Curso.objects.get(nombre="CURSO4").pk
        anio_lectivo = AnioLectivo.objects.get(nombre="2020").pk
        data = [
            {
                "alumno": alumno_2,
                "curso": curso,
                "anio_lectivo": anio_lectivo,
            },
            {
                "alumno": alumno_1,
                "curso": curso,
                "anio_lectivo": anio_lectivo,
            },
        ]
        response = self.client.post(
            "/api/alumnos/curso/multiple/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "No se puede asignar un alumno a dos cursos distintos en un Año Lectivo",
        )

    def test_create_alumno_curso_admin(self):
        """
        Test de creacion correcta de AlumnoCurso por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        alumno = Alumno.objects.get(apellido="3").pk
        curso = Curso.objects.get(nombre="CURSO2").pk
        anio_lectivo = AnioLectivo.objects.get(nombre="2019").pk
        data = {
            "alumno": alumno,
            "curso": curso,
            "anio_lectivo": anio_lectivo,
        }
        response = self.client.post("/api/alumnos/curso/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_alumno_curso_docente(self):
        """
        Test de creacion correcta de AlumnoCurso por docente
        """
        self.client.force_authenticate(user=self.user_docente)
        alumno = Alumno.objects.get(apellido="3").pk
        curso = Curso.objects.get(nombre="CURSO2").pk
        anio_lectivo = AnioLectivo.objects.get(nombre="2019").pk
        data = {
            "alumno": alumno,
            "curso": curso,
            "anio_lectivo": anio_lectivo,
        }
        response = self.client.post("/api/alumnos/curso/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_alumno_curso_conflicto(self):
        """
        Test de creacion con conflictos por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        data = {
            "alumno": 2,
            "curso": 2,
            "anio_lectivo": 2,
        }
        response = self.client.post("/api/alumnos/curso/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "No se puede asignar un alumno a dos cursos distintos en un Año Lectivo",
        )

        data = {
            "alumno": 1,
            "curso": 2,
            "anio_lectivo": 1,
        }
        response = self.client.post("/api/alumnos/curso/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "No se puede asignar un alumno a dos cursos distintos en un Año Lectivo",
        )

        data = {
            "alumno": 1,
            "curso": 2,
            "anio_lectivo": 3,
        }
        response = self.client.post("/api/alumnos/curso/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

        data = {
            "alumno": 20,
            "curso": 2,
            "anio_lectivo": 2,
        }
        response = self.client.post("/api/alumnos/curso/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

        data = {
            "alumno": 1,
            "curso": 3,
            "anio_lectivo": 2,
        }
        response = self.client.post("/api/alumnos/curso/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

        data = {
            "alumno": 1,
            "curso": 3,
        }
        response = self.client.post("/api/alumnos/curso/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_alumno_curso_admin(self):
        """
        Test de obtencion correcta de AlumnoCurso por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.get("/api/alumnos/curso/1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_alumno_curso_admin_incorrect(self):
        """
        Test de obtencion incorrecta de AlumnoCurso por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.get("/api/alumnos/curso/7/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get("/api/alumnos/curso/20/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_alumno_curso_docente(self):
        """
        Test de obtencion correcta de AlumnoCurso por docente
        """
        self.client.force_authenticate(user=self.user_docente)
        response = self.client.get("/api/alumnos/curso/1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_alumno_curso_admin(self):
        """
        Test de listado correcto de AlumnoCurso por admin
        """
        self.client.force_authenticate(user=self.user_admin)

        curso_1 = self.curso_1.id
        curso_3 = self.curso_3.id
        alumno = self.alumno_1.id
        anio_lectivo_2 = self.anio_lectivo_2.id
        anio_lectivo_1 = self.anio_lectivo_1.id

        response = self.client.get("/api/alumnos/curso/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 6)

        response = self.client.get(f"/api/alumnos/curso/list/?curso={curso_1}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

        response = self.client.get("/api/alumnos/curso/list/?curso=x")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["curso"], "El valor no es numérico")

        response = self.client.get(f"/api/alumnos/curso/list/?curso={curso_3}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

        response = self.client.get(
            f"/api/alumnos/curso/list/?anio_lectivo={anio_lectivo_2}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

        response = self.client.get(f"/api/alumnos/curso/list/?alumno={alumno}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        response = self.client.get(
            f"/api/alumnos/curso/list/?curso={curso_1}&anio_lectivo={anio_lectivo_1}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_list_alumno_curso_docente(self):
        """
        Test de listado correcto de AlumnoCurso por docente
        """
        self.client.force_authenticate(user=self.user_docente)
        response = self.client.get("/api/alumnos/curso/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 6)

    def test_destroy_alumno_curso_admin(self):
        """
        Test de borrado correcto de AlumnoCurso por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.delete("/api/alumnos/curso/1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get("/api/alumnos/curso/list/")
        self.assertEqual(response.data["count"], 5)

    def test_destroy_alumno_curso_docente(self):
        """
        Test de borrado de AlumnoCurso por docente
        """
        self.client.force_authenticate(user=self.user_docente)
        response = self.client.delete("/api/alumnos/curso/1/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get("/api/alumnos/curso/list/")
        self.assertEqual(response.data["count"], 6)

    def test_destroy_alumno_curso_admin_incorrecto(self):
        """
        Test de borrado incorrecto de AlumnoCurso por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.delete("/api/alumnos/curso/7/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete("/api/alumnos/curso/20/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

