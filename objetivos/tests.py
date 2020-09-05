from django.test import TestCase
from django.contrib.auth.models import Permission
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from users.models import User, Group
from instituciones.models import Institucion
from curricula.models import Carrera, AnioLectivo, Curso, Anio, Materia
from alumnos.models import Alumno, AlumnoCurso
from objetivos.models import Objetivo, AlumnoObjetivo, TipoObjetivo
from seguimientos.models import (
    Seguimiento,
    IntegranteSeguimiento,
    RolSeguimiento,
)
from rest_framework import status
import datetime
from collections import OrderedDict

# from rest_framework.utils.serializer_helpers import ReturnList

# Create your tests here.
class ObjetivoTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup de User y permisos para poder ejecutar todas las acciones
        """
        cls.client = APIClient()
        cls.group_admin = Group.objects.create(name="Admin")
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can add objetivo")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can change objetivo")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can delete objetivo")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Puede listar objetivos")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can view objetivo")
        )
        cls.group_admin.save()

        cls.group_docente = Group.objects.create(name="Docente")
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Puede listar objetivos")
        )
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Can view objetivo")
        )
        cls.group_docente.save()

        cls.institucion_1 = Institucion.objects.create(nombre="Institucion_1")
        cls.institucion_2 = Institucion.objects.create(nombre="Institucion_2")

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
        cls.user_admin_2 = User.objects.create_user(
            "admin2@admin.com",
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

        cls.alumno_2 = Alumno.objects.create(
            dni=2,
            nombre="Alumno2",
            apellido="2",
            institucion=cls.institucion_1,
        )

        cls.alumno_curso_1 = AlumnoCurso.objects.create(
            alumno=cls.alumno_1,
            curso=cls.curso_1,
            anio_lectivo=cls.anio_lectivo_1,
        )

        cls.alumno_curso_2 = AlumnoCurso.objects.create(
            alumno=cls.alumno_2,
            curso=cls.curso_1,
            anio_lectivo=cls.anio_lectivo_1,
        )

        cls.materia_1 = Materia.objects.create(
            nombre="Matematicas", anio=cls.anio_1
        )

        cls.materia_2 = Materia.objects.create(
            nombre="Lengua", anio=cls.anio_1
        )

        cls.seguimiento_1 = Seguimiento.objects.create(
            nombre="seguimiento_1",
            en_progreso=True,
            institucion=cls.institucion_1,
            fecha_inicio=datetime.date(2020, 1, 1),
            fecha_cierre=datetime.date(2020, 12, 31),
            descripcion=".",
            anio_lectivo=cls.anio_lectivo_1,
            encargado=cls.user_admin,
        )
        cls.seguimiento_1.alumnos.add(cls.alumno_curso_1, cls.alumno_curso_2)
        cls.seguimiento_1.materias.add(cls.materia_1, cls.materia_2)
        cls.seguimiento_1.save()

        cls.seguimiento_2 = Seguimiento.objects.create(
            nombre="seguimiento_2",
            en_progreso=False,
            institucion=cls.institucion_1,
            fecha_inicio=datetime.date(2020, 1, 1),
            fecha_cierre=datetime.date(2020, 12, 31),
            descripcion=".",
            anio_lectivo=cls.anio_lectivo_1,
            encargado=cls.user_admin,
        )
        cls.seguimiento_2.alumnos.add(cls.alumno_curso_1, cls.alumno_curso_2)
        cls.seguimiento_2.materias.add(cls.materia_1, cls.materia_2)
        cls.seguimiento_2.save()

        cls.seguimiento_3 = Seguimiento.objects.create(
            nombre="seguimiento_3",
            en_progreso=True,
            institucion=cls.institucion_2,
            fecha_inicio=datetime.date(2020, 1, 1),
            fecha_cierre=datetime.date(2020, 12, 31),
            descripcion=".",
            anio_lectivo=cls.anio_lectivo_1,
            encargado=cls.user_admin,
        )

        cls.seguimiento_4 = Seguimiento.objects.create(
            nombre="seguimiento_4",
            en_progreso=True,
            institucion=cls.institucion_1,
            fecha_inicio=datetime.date(2020, 1, 1),
            fecha_cierre=datetime.date(2020, 12, 31),
            descripcion=".",
            anio_lectivo=cls.anio_lectivo_1,
            encargado=cls.user_admin,
        )

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

        cls.integrante_2 = IntegranteSeguimiento.objects.create(
            seguimiento=cls.seguimiento_1,
            usuario=cls.user_docente,
            rol=cls.rol_2,
            fecha_desde=datetime.date(2020, 1, 1),
        )

        cls.integrante_3 = IntegranteSeguimiento.objects.create(
            seguimiento=cls.seguimiento_1,
            usuario=cls.user_admin_2,
            rol=cls.rol_1,
            fecha_desde=datetime.date(2020, 1, 1),
            fecha_hasta=datetime.date(2020, 2, 15),
        )

        cls.integrante_4 = IntegranteSeguimiento.objects.create(
            seguimiento=cls.seguimiento_2,
            usuario=cls.user_admin,
            rol=cls.rol_1,
            fecha_desde=datetime.date(2020, 1, 1),
        )

        cls.integrante_5 = IntegranteSeguimiento.objects.create(
            seguimiento=cls.seguimiento_4,
            usuario=cls.user_admin,
            rol=cls.rol_2,
            fecha_desde=datetime.date(2020, 1, 1),
        )

        cls.integrante_6 = IntegranteSeguimiento.objects.create(
            seguimiento=cls.seguimiento_4,
            usuario=cls.user_docente,
            rol=cls.rol_1,
            fecha_desde=datetime.date(2020, 1, 1),
        )

        cls.integrante_7 = IntegranteSeguimiento.objects.create(
            seguimiento=cls.seguimiento_3,
            usuario=cls.user_admin,
            rol=cls.rol_1,
            fecha_desde=datetime.date(2020, 1, 1),
        )

        cls.tipo_objetivo_1 = TipoObjetivo.objects.create(
            nombre="Cualitativo", cuantitativo=False, multiple=True,
        )

        cls.tipo_objetivo_1 = TipoObjetivo.objects.create(
            nombre="Cualitativo", cuantitativo=False, multiple=True,
        )
        cls.tipo_objetivo_2 = TipoObjetivo.objects.create(
            nombre="Promedio notas",
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
            descripcion="conductaa",
            seguimiento=cls.seguimiento_3,
            tipo_objetivo=cls.tipo_objetivo_1,
        )
        cls.objetivo_4 = Objetivo.objects.create(
            descripcion="conductaaa",
            seguimiento=cls.seguimiento_4,
            tipo_objetivo=cls.tipo_objetivo_1,
        )
        cls.objetivo_5 = Objetivo.objects.create(
            descripcion="conductaaa",
            seguimiento=cls.seguimiento_2,
            tipo_objetivo=cls.tipo_objetivo_1,
        )

        cls.alumno_objetivo_1 = AlumnoObjetivo.objects.create(
            objetivo=cls.objetivo_2,
            alumno_curso=cls.alumno_curso_1,
            valor=65,
            alcanzada=False,
        )
        cls.alumno_objetivo_2 = AlumnoObjetivo.objects.create(
            objetivo=cls.objetivo_2,
            alumno_curso=cls.alumno_curso_2,
            valor=50,
            alcanzada=False,
        )

    #############
    #   CREATE  #
    #############

    def test_create_objetivo_admin(self):
        """
        Test de creacion correcta de Objetivo por admin
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento = self.seguimiento_1.id
        tipo_objetivo = self.tipo_objetivo_3.id
        data = {
            "valor_objetivo_cuantitativo": 85,
            "seguimiento": seguimiento,
            "tipo_objetivo": tipo_objetivo,
        }
        response = self.client.post("/api/objetivos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["id"])

    def test_create_objetivo_docente(self):
        """
        Test de creacion de Objetivo por docente
        """
        self.client.force_authenticate(user=self.user_docente)
        seguimiento = self.seguimiento_4.id
        tipo_objetivo = self.tipo_objetivo_3.id
        data = {
            "valor_objetivo_cuantitativo": 85,
            "seguimiento": seguimiento,
            "tipo_objetivo": tipo_objetivo,
        }
        response = self.client.post("/api/objetivos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_objetivo_otra_institucion(self):
        """
        Test de creacion de Objetivo para un seguimiento de otra institucion
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento = self.seguimiento_3.id
        tipo_objetivo = self.tipo_objetivo_3.id
        data = {
            "valor_objetivo_cuantitativo": 85,
            "seguimiento": seguimiento,
            "tipo_objetivo": tipo_objetivo,
        }
        response = self.client.post("/api/objetivos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

    def test_create_objetivo_no_en_progreso(self):
        """
        Test de creacion de Objetivo para un seguimiento que no está en progreso
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento = self.seguimiento_2.id
        tipo_objetivo = self.tipo_objetivo_3.id
        data = {
            "valor_objetivo_cuantitativo": 85,
            "seguimiento": seguimiento,
            "tipo_objetivo": tipo_objetivo,
        }
        response = self.client.post("/api/objetivos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "No se puede modificar un Seguimiento que no se encuentra en progreso",
        )

    def test_create_objetivo_no_integrante(self):
        """
        Test de creacion de Objetivo para un seguimiento del que no es integrante
        """
        self.client.force_authenticate(user=self.user_admin_2)
        seguimiento = self.seguimiento_2.id
        tipo_objetivo = self.tipo_objetivo_3.id
        data = {
            "valor_objetivo_cuantitativo": 85,
            "seguimiento": seguimiento,
            "tipo_objetivo": tipo_objetivo,
        }
        response = self.client.post("/api/objetivos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

    def test_create_objetivo_no_encargado(self):
        """
        Test de creacion de Objetivo para un seguimiento del que no es encargado
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento = self.seguimiento_4.id
        tipo_objetivo = self.tipo_objetivo_3.id
        data = {
            "valor_objetivo_cuantitativo": 85,
            "seguimiento": seguimiento,
            "tipo_objetivo": tipo_objetivo,
        }
        response = self.client.post("/api/objetivos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "No tiene permiso para crear un objetivo"
        )

    def test_create_objetivo_cualitativo_sin_descripcion(self):
        """
        Test de creacion de Objetivo cualitativo sin descripción
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento = self.seguimiento_1.id
        tipo_objetivo = self.tipo_objetivo_1.id
        data = {
            "valor_objetivo_cuantitativo": 85,
            "seguimiento": seguimiento,
            "tipo_objetivo": tipo_objetivo,
        }
        response = self.client.post("/api/objetivos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Para este tipo de objetivos es necesario fijar una descripción",
        )

    def test_create_objetivo_cuantitativo_sin_valor(self):
        """
        Test de creacion de Objetivo cuantitativo sin valor
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento = self.seguimiento_1.id
        tipo_objetivo = self.tipo_objetivo_3
        data = {
            "seguimiento": seguimiento,
            "tipo_objetivo": tipo_objetivo.id,
        }
        response = self.client.post("/api/objetivos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            f"No se ingreso un valor, o no se encuentra en el rango permitido de {float(tipo_objetivo.valor_minimo)} a {float(tipo_objetivo.valor_maximo)}",
        )

    def test_create_objetivo_cuantitativo_fuera_rango(self):
        """
        Test de creacion de Objetivo cuantitativo valor fuera de rango
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento = self.seguimiento_1.id
        tipo_objetivo = self.tipo_objetivo_3
        data = {
            "valor_objetivo_cuantitativo": 120,
            "seguimiento": seguimiento,
            "tipo_objetivo": tipo_objetivo.id,
        }
        response = self.client.post("/api/objetivos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            f"No se ingreso un valor, o no se encuentra en el rango permitido de {float(tipo_objetivo.valor_minimo)} a {float(tipo_objetivo.valor_maximo)}",
        )

    def test_create_objetivo_cuantitativo_no_multiple(self):
        """
        Test de creacion de Objetivo cuantitativo no multiple
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento = self.seguimiento_1.id
        tipo_objetivo = self.tipo_objetivo_2
        data = {
            "valor_objetivo_cuantitativo": 90,
            "seguimiento": seguimiento,
            "tipo_objetivo": tipo_objetivo.id,
        }
        response = self.client.post("/api/objetivos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Ya existe un objetivo de este mismo tipo en el seguimiento. No está permitido tener dos objetivos del mismo tipo",
        )

    def test_create_objetivo_tipo_no_existente(self):
        """
        Test de creacion de Objetivo cuantitativo con tipo no existente
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento = self.seguimiento_1.id
        tipo_objetivo = 500
        data = {
            "valor_objetivo_cuantitativo": 90,
            "seguimiento": seguimiento,
            "tipo_objetivo": tipo_objetivo,
        }
        response = self.client.post("/api/objetivos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_objetivo_seguimiento_no_existente(self):
        """
        Test de creacion de Objetivo cuantitativo con seguimiento no existente
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento = 500
        tipo_objetivo = self.tipo_objetivo_1.id
        data = {
            "valor_objetivo_cuantitativo": 90,
            "seguimiento": seguimiento,
            "tipo_objetivo": tipo_objetivo,
        }
        response = self.client.post("/api/objetivos/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #############
    #   UPDATE  #
    #############

    def test_update_objetivo_cualitativo(self):
        """
        Test de modificación de Objetivo cualitativo
        """
        self.client.force_authenticate(user=self.user_admin)
        objetivo_id = self.objetivo_1.id
        data = {
            "valor_objetivo_cuantitativo": 85,
            "descripcion": "Cualitativo 2",
        }
        response = self.client.patch(
            f"/api/objetivos/{objetivo_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        objetivo = Objetivo.objects.get(pk=objetivo_id)
        self.assertEqual(objetivo.descripcion, "Cualitativo 2")
        self.assertIsNone(objetivo.valor_objetivo_cuantitativo)

    def test_update_objetivo_cuantitativo(self):
        """
        Test de modificación de Objetivo cuantitativo
        """
        self.client.force_authenticate(user=self.user_admin)
        objetivo_id = self.objetivo_2.id
        data = {
            "valor_objetivo_cuantitativo": 60,
        }
        response = self.client.patch(
            f"/api/objetivos/{objetivo_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        objetivo = Objetivo.objects.get(pk=objetivo_id)
        self.assertEqual(objetivo.valor_objetivo_cuantitativo, 60)
        objetivo_alumno_1 = AlumnoObjetivo.objects.get(
            pk=self.alumno_objetivo_1.id
        )
        self.assertTrue(objetivo_alumno_1.alcanzada)
        objetivo_alumno_2 = AlumnoObjetivo.objects.get(
            pk=self.alumno_objetivo_2.id
        )
        self.assertFalse(objetivo_alumno_2.alcanzada)

    def test_update_objetivo_cuantitativo_valor_fuera_rango(self):
        """
        Test de modificación de Objetivo cuantitativo con su valor fuera de rango
        """
        self.client.force_authenticate(user=self.user_admin)
        objetivo_id = self.objetivo_2.id
        tipo_objetivo = self.tipo_objetivo_2
        data = {
            "valor_objetivo_cuantitativo": 110,
        }
        response = self.client.patch(
            f"/api/objetivos/{objetivo_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            f"No se encuentra en el rango permitido de {float(tipo_objetivo.valor_minimo)} a {float(tipo_objetivo.valor_maximo)}",
        )

    def test_update_objetivo_no_existente(self):
        """
        Test de modificación de Objetivo no existente
        """
        self.client.force_authenticate(user=self.user_admin)
        objetivo_id = 500
        data = {
            "valor_objetivo_cuantitativo": 110,
        }
        response = self.client.patch(
            f"/api/objetivos/{objetivo_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["detail"], "No encontrado.",
        )

    def test_update_objetivo_no_integrante(self):
        """
        Test de modificación de Objetivo de un seguimiento del cual no se es parte
        """
        self.client.force_authenticate(user=self.user_admin_2)
        objetivo_id = self.objetivo_4.id
        data = {
            "descripcion": "desc",
        }
        response = self.client.patch(
            f"/api/objetivos/{objetivo_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["detail"], "No encontrado.",
        )

    def test_update_objetivo_docente(self):
        """
        Test de modificación de Objetivo docente
        """
        self.client.force_authenticate(user=self.user_docente)
        objetivo_id = self.objetivo_1.id
        data = {
            "decripcion": "desc",
        }
        response = self.client.patch(
            f"/api/objetivos/{objetivo_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_objetivo_no_encargado(self):
        """
        Test de modificación de Objetivo sin ser encargado
        """
        self.client.force_authenticate(user=self.user_admin)
        objetivo_id = self.objetivo_4.id
        data = {
            "decripcion": "desc",
        }
        response = self.client.patch(
            f"/api/objetivos/{objetivo_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "No tiene permiso para modificar el objetivo",
        )

    def test_update_objetivo_otra_institucion(self):
        """
        Test de modificación de Objetivo de otra institucion
        """
        self.client.force_authenticate(user=self.user_admin)
        objetivo_id = self.objetivo_3.id
        data = {
            "decripcion": "desc",
        }
        response = self.client.patch(
            f"/api/objetivos/{objetivo_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["detail"], "No encontrado.",
        )

    def test_update_objetivo_no_en_progreso(self):
        """
        Test de modificación de Objetivo de un seguimiento que no está en progreso
        """
        self.client.force_authenticate(user=self.user_admin)
        objetivo_id = self.objetivo_5.id
        data = {
            "decripcion": "desc",
        }
        response = self.client.patch(
            f"/api/objetivos/{objetivo_id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "No se puede modificar un Seguimiento que no se encuentra en progreso",
        )

    #############
    #    LIST   #
    #############

    def test_list_correcto(self):
        """
        Test de listado de Objetivo correcto
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento_id = self.seguimiento_1.id
        response = self.client.get(
            f"/api/objetivos/list/seguimiento/{seguimiento_id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_no_existente(self):
        """
        Test de listado de Objetivo con seguimiento no existente
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento_id = 2000
        response = self.client.get(
            f"/api/objetivos/list/seguimiento/{seguimiento_id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

    def test_list_otra_institucion(self):
        """
        Test de listado de Objetivo de un seguimiento de otra institucion
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento_id = self.seguimiento_3.id
        response = self.client.get(
            f"/api/objetivos/list/seguimiento/{seguimiento_id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

    def test_list_no_integrante(self):
        """
        Test de listado de Objetivo no integrante
        """
        self.client.force_authenticate(user=self.user_admin_2)
        seguimiento_id = self.seguimiento_4.id
        response = self.client.get(
            f"/api/objetivos/list/seguimiento/{seguimiento_id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

    #############
    #   DELETE  #
    #############

    def test_delete_correcto(self):
        """
        Test de borrado de Objetivo correcto
        """
        self.client.force_authenticate(user=self.user_admin)
        objetivo_id = self.objetivo_1.id
        response = self.client.delete(f"/api/objetivos/{objetivo_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_no_existente(self):
        """
        Test de borrado de Objetivo no existente
        """
        self.client.force_authenticate(user=self.user_admin)
        objetivo_id = 5000
        response = self.client.delete(f"/api/objetivos/{objetivo_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

    def test_delete_otra_institucion(self):
        """
        Test de borrado de Objetivo de un seguimiento de otra institucion
        """
        self.client.force_authenticate(user=self.user_admin)
        objetivo_id = self.objetivo_3.id
        response = self.client.delete(f"/api/objetivos/{objetivo_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

    def test_delete_no_integrante(self):
        """
        Test de borrado de Objetivo no integrante
        """
        self.client.force_authenticate(user=self.user_admin_2)
        objetivo_id = self.objetivo_4.id
        response = self.client.delete(f"/api/objetivos/{objetivo_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

    def test_delete_no_encargado(self):
        """
        Test de borrado de Objetivo no encargado
        """
        self.client.force_authenticate(user=self.user_admin)
        objetivo_id = self.objetivo_4.id
        response = self.client.delete(f"/api/objetivos/{objetivo_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "No tiene permiso para borrar un objetivo"
        )

    def test_delete_no_en_progreso(self):
        """
        Test de listado de Objetivo no en progreso
        """
        self.client.force_authenticate(user=self.user_admin)
        objetivo_id = self.objetivo_5.id
        response = self.client.delete(f"/api/objetivos/{objetivo_id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "No se puede modificar un Seguimiento que no se encuentra en progreso",
        )

    #############
    #    GET    #
    #############

    def test_get_correcto(self):
        """
        Test de obtencion de Objetivo correcto
        """
        self.client.force_authenticate(user=self.user_admin)
        objetivo_id = self.objetivo_1.id
        response = self.client.get(f"/api/objetivos/{objetivo_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_no_existente(self):
        """
        Test de obtencion de Objetivo no existente
        """
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.get(f"/api/objetivos/600/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

    def test_get_otra_institucion(self):
        """
        Test de obtencion de Objetivo de otra institucion
        """
        self.client.force_authenticate(user=self.user_admin)
        objetivo_id = self.objetivo_3.id
        response = self.client.get(f"/api/objetivos/{objetivo_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")

    def test_get_no_integrante(self):
        """
        Test de obtencion de Objetivo no integrante
        """
        self.client.force_authenticate(user=self.user_admin_2)
        objetivo_id = self.objetivo_4.id
        response = self.client.get(f"/api/objetivos/{objetivo_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No encontrado.")


class AlumnoObjetivoTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup de User y permisos para poder ejecutar todas las acciones
        """
        cls.client = APIClient()
        cls.group_admin = Group.objects.create(name="Admin")
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Puede listar alumno_objetivo")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can change alumno objetivo")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can view alumno objetivo")
        )
        cls.group_admin.save()

        cls.group_docente = Group.objects.create(name="Docente")
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Puede listar alumno_objetivo")
        )
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Can view alumno objetivo")
        )
        cls.group_docente.save()

        cls.institucion_1 = Institucion.objects.create(nombre="Institucion_1")
        cls.institucion_2 = Institucion.objects.create(nombre="Institucion_2")

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

        cls.alumno_2 = Alumno.objects.create(
            dni=2,
            nombre="Alumno2",
            apellido="2",
            institucion=cls.institucion_1,
        )

        cls.alumno_3 = Alumno.objects.create(
            dni=3,
            nombre="Alumno3",
            apellido="3",
            institucion=cls.institucion_2,
        )

        cls.alumno_curso_1 = AlumnoCurso.objects.create(
            alumno=cls.alumno_1,
            curso=cls.curso_1,
            anio_lectivo=cls.anio_lectivo_1,
        )

        cls.alumno_curso_2 = AlumnoCurso.objects.create(
            alumno=cls.alumno_2,
            curso=cls.curso_1,
            anio_lectivo=cls.anio_lectivo_1,
        )

        cls.materia_1 = Materia.objects.create(
            nombre="Matematicas", anio=cls.anio_1
        )

        cls.materia_2 = Materia.objects.create(
            nombre="Lengua", anio=cls.anio_1
        )

        cls.seguimiento_1 = Seguimiento.objects.create(
            nombre="seguimiento_1",
            en_progreso=True,
            institucion=cls.institucion_1,
            fecha_inicio=datetime.date(2020, 1, 1),
            fecha_cierre=datetime.date(2020, 12, 31),
            descripcion=".",
            anio_lectivo=cls.anio_lectivo_1,
            encargado=cls.user_admin,
        )
        cls.seguimiento_1.alumnos.add(cls.alumno_curso_1, cls.alumno_curso_2)
        cls.seguimiento_1.materias.add(cls.materia_1, cls.materia_2)
        cls.seguimiento_1.save()

        cls.seguimiento_2 = Seguimiento.objects.create(
            nombre="seguimiento_2",
            en_progreso=False,
            institucion=cls.institucion_1,
            fecha_inicio=datetime.date(2020, 1, 1),
            fecha_cierre=datetime.date(2020, 12, 31),
            descripcion=".",
            anio_lectivo=cls.anio_lectivo_1,
            encargado=cls.user_admin,
        )
        cls.seguimiento_2.alumnos.add(cls.alumno_curso_1, cls.alumno_curso_2)
        cls.seguimiento_2.materias.add(cls.materia_1, cls.materia_2)
        cls.seguimiento_2.save()

        cls.seguimiento_3 = Seguimiento.objects.create(
            nombre="seguimiento_3",
            en_progreso=True,
            institucion=cls.institucion_2,
            fecha_inicio=datetime.date(2020, 1, 1),
            fecha_cierre=datetime.date(2020, 12, 31),
            descripcion=".",
            anio_lectivo=cls.anio_lectivo_1,
            encargado=cls.user_admin,
        )

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

        cls.integrante_2 = IntegranteSeguimiento.objects.create(
            seguimiento=cls.seguimiento_1,
            usuario=cls.user_docente,
            rol=cls.rol_2,
            fecha_desde=datetime.date(2020, 1, 1),
        )

        cls.tipo_objetivo_1 = TipoObjetivo.objects.create(
            nombre="Cualitativo", cuantitativo=False, multiple=True,
        )

        cls.tipo_objetivo_2 = TipoObjetivo.objects.create(
            nombre="Promedio notas",
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
            seguimiento=cls.seguimiento_3,
            tipo_objetivo=cls.tipo_objetivo_2,
        )

        cls.alumno_objetivo_1 = AlumnoObjetivo.objects.create(
            objetivo=cls.objetivo_2,
            alumno_curso=cls.alumno_curso_1,
            valor=65,
            alcanzada=False,
        )
        cls.alumno_objetivo_2 = AlumnoObjetivo.objects.create(
            objetivo=cls.objetivo_2,
            alumno_curso=cls.alumno_curso_2,
            valor=50,
            alcanzada=False,
        )
        cls.alumno_objetivo_3 = AlumnoObjetivo.objects.create(
            objetivo=cls.objetivo_1,
            alumno_curso=cls.alumno_curso_1,
            alcanzada=True,
        )

    #############
    #    GET    #
    #############

    def test_get_correcto(self):
        """
        Test de obtencion de AlumnoObjetivo correcto
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento = self.seguimiento_1.id
        objetivo = self.objetivo_1.id

        response = self.client.get(
            f"/api/objetivos/alumno/{self.alumno_1.id}/?objetivo={objetivo}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, dict))

        response = self.client.get(
            f"/api/objetivos/alumno/{self.alumno_1.id}/?seguimiento={seguimiento}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(len(response.data), 2)

    def test_get_seguimiento_y_objetivo(self):
        """
        Test de obtencion de AlumnoObjetivo con seguimiento y objetivo
        """
        self.client.force_authenticate(user=self.user_admin)
        seguimiento = self.seguimiento_1.id
        objetivo = self.objetivo_1.id

        response = self.client.get(
            f"/api/objetivos/alumno/{self.alumno_1.id}/?objetivo={objetivo}&seguimiento={seguimiento}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "No se puede obtener por seguimiento y objetivo al mismo tiempo",
        )

    def test_get_sin_seguimiento_ni_objetivo(self):
        """
        Test de obtencion de AlumnoObjetivo sin seguimiento ni objetivo
        """
        self.client.force_authenticate(user=self.user_admin)

        response = self.client.get(
            f"/api/objetivos/alumno/{self.alumno_1.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Es necesario pasar o seguimiento u objetivo",
        )

    def test_get_alumno_no_existente_u_otra_institucion(self):
        """
        Test de obtencion de AlumnoObjetivo con alumno no existente o de otra institucion
        """
        self.client.force_authenticate(user=self.user_admin)
        objetivo = self.objetivo_1.id

        response = self.client.get(
            f"/api/objetivos/alumno/5000/?objetivo={objetivo}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["detail"], "No encontrado.",
        )

        response = self.client.get(
            f"/api/objetivos/alumno/{self.alumno_3.id}/?objetivo={objetivo}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["detail"], "No encontrado.",
        )

    def test_get_seguimiento_no_existente_u_otra_institucion(self):
        """
        Test de obtencion de AlumnoObjetivo con seguimiento no existente o de otra institucion
        """
        self.client.force_authenticate(user=self.user_admin)

        response = self.client.get(
            f"/api/objetivos/alumno/{self.alumno_1.id}/?seguimiento={self.seguimiento_3.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["detail"], "No encontrado.",
        )

        response = self.client.get(
            f"/api/objetivos/alumno/{self.alumno_1.id}/?seguimiento=5000"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["detail"], "No encontrado.",
        )

    def test_get_objetivo_no_existente_u_otra_institucion(self):
        """
        Test de obtencion de AlumnoObjetivo con objetivo no existente o de otra institucion
        """
        self.client.force_authenticate(user=self.user_admin)

        response = self.client.get(
            f"/api/objetivos/alumno/{self.alumno_1.id}/?objetivo={self.objetivo_3.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["detail"], "No encontrado.",
        )

        response = self.client.get(
            f"/api/objetivos/alumno/{self.alumno_1.id}/?objetivo=5000"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["detail"], "No encontrado.",
        )

