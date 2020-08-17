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

# from rest_framework.utils.serializer_helpers import ReturnList

# Create your tests here.
class AsistenciaTests(APITestCase):
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

        cls.alumno_objetivo_1 = AlumnoObjetivo.objects.create(
            objetivo=cls.objetivo_2,
            alumno_curso=cls.alumno_curso_1,
            valor=65,
            alcanzada=False,
        )

    #############
    #  CREATE + #
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
