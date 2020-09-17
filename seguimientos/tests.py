from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework.utils.serializer_helpers import ReturnList
from users.models import User, Group
from django.contrib.auth.models import Permission
from seguimientos.models import (
    Seguimiento,
    RolSeguimiento,
    SolicitudSeguimiento,
    FechaEstadoSolicitudSeguimiento,
    EstadoSolicitudSeguimiento,
)
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
import logging


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
        cls.institucion = Institucion.objects.create(
            nombre="MIT", identificador="1234"
        )
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
        cls.rol_tutor = RolSeguimiento.objects.create(nombre="Tutor")

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

        cls.materia2 = Materia.objects.create(
            **{"nombre": "Análisis Matemático 2", "anio_id": cls.anio.pk}
        )

        cls.materia3 = Materia.objects.create(
            **{"nombre": "Análisis Matemático 3", "anio_id": cls.anio.pk}
        )

        cls.evaluacion1 = Evaluacion.objects.create(
            **{
                "anio_lectivo": cls.anio_lectivo,
                "materia": cls.materia,
                "ponderacion": 0.5,
                "nombre": "Primera",
            }
        )
        cls.evaluacion2 = Evaluacion.objects.create(
            **{
                "anio_lectivo": cls.anio_lectivo,
                "materia": cls.materia,
                "ponderacion": 0.3,
                "nombre": "Segunda",
            }
        )
        cls.evaluacion3 = Evaluacion.objects.create(
            **{
                "anio_lectivo": cls.anio_lectivo,
                "materia": cls.materia,
                "ponderacion": 0.2,
                "nombre": "Tercera",
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
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
                {"usuario": self.user_docente.pk, "rol": self.rol_profesor.pk},
            ],
            "fecha_cierre": "12/12/2021",
            "materias": [self.materia.pk],
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Seguimiento.objects.count(), 1)
        self.assertEqual(
            Seguimiento.objects.get().nombre, "PRIMER SEGUIMIENTO"
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
            "fecha_cierre": "12/12/2021",
            "materias": [self.materia.pk],
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Seguimiento.objects.count(), 1)
        self.assertEqual(
            Seguimiento.objects.get().nombre, "PRIMER SEGUIMIENTO"
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
            "materias": [self.materia.pk],
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
                {"usuario": self.user_docente.pk, "rol": self.rol_profesor.pk},
            ],
            "fecha_cierre": "12/12/2021",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Seguimiento.objects.count(), 1)
        self.assertEqual(
            Seguimiento.objects.get().nombre, "PRIMER SEGUIMIENTO"
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

    def test_create_seguimiento_con_materias_unica(self):
        """
        Test de creacion de seguimientos + materias unica
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "fecha_cierre": "12/12/2021",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "materias": [self.materia.pk],
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
                {"usuario": self.user_docente.pk, "rol": self.rol_profesor.pk},
            ],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Seguimiento.objects.count(), 1)
        self.assertEqual(
            Seguimiento.objects.get().nombre, "PRIMER SEGUIMIENTO"
        )

    def test_create_seguimiento_sin_encargado(self):
        """
        Test de creacion de seguimientos invalido
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "fecha_cierre": "12/12/2021",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "materias": [self.materia.pk, self.materia2.pk, self.materia3.pk],
            "integrantes": [
                {"usuario": self.user_docente.pk, "rol": self.rol_profesor.pk},
            ],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Seguimiento.objects.count(), 0)

    def test_create_seguimiento_sin_integrantes(self):
        """
        Test de creacion de seguimientos invalido
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "fecha_cierre": "12/12/2021",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "materias": [self.materia.pk, self.materia2.pk, self.materia3.pk],
            "integrantes": [],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Seguimiento.objects.count(), 0)

    def test_create_seguimiento_con_materias_parciales(self):
        """
        Test de creacion de seguimientos + materias parciales
        Esto es inválido
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "materias": [self.materia.pk, self.materia2.pk],
            "fecha_cierre": "12/12/2021",
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
                {"usuario": self.user_docente.pk, "rol": self.rol_profesor.pk},
            ],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Seguimiento.objects.count(), 0)
        self.assertEqual(
            response.data["detail"][0],
            "Se deben elegir o una materia o todas las del año",
        )

    def test_create_seguimiento_con_fecha_cierre(self):
        """
        Test de creacion de seguimientos + fecha_cierre
        Fecha válida ya que es en futuro
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "fecha_cierre": "12/12/2021",
            "materias": [self.materia.pk, self.materia2.pk, self.materia3.pk],
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
                {"usuario": self.user_docente.pk, "rol": self.rol_profesor.pk},
            ],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Seguimiento.objects.count(), 1)

    def test_create_seguimiento_con_fecha_cierre_invalida(self):
        """
        Tes t de creacion de seguimientos + fecha_cierre invalida
        Fecha inválida ya que es previa al comienzo

        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "fecha_cierre": "12/12/1999",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Seguimiento.objects.count(), 0)

    def test_list_seguimiento(self):
        """
        Test de listado de seguimientos solo en progreso
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "fecha_cierre": "12/12/2020",
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
            ],
            "materias": [self.materia.pk],
        }
        self.client.post(url, data, format="json")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Segundo Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "fecha_cierre": "12/12/2020",
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
            ],
            "materias": [self.materia.pk],
        }
        self.client.post(url, data, format="json")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Tercer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "fecha_cierre": "12/12/2020",
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
            ],
            "materias": [self.materia.pk],
        }
        self.client.post(url, data, format="json")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Cuarto Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "fecha_cierre": "12/12/2020",
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
            ],
            "materias": [self.materia.pk],
        }
        response = self.client.post(url, data, format="json")
        data = {
            "en_progreso": False,
        }
        response = self.client.patch(
            f"/api/seguimientos/{response.data['id']}/status/",
            data,
            format="json",
        )
        response = self.client.get("/api/seguimientos/list/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_list_seguimiento_w_cerrados(self):
        """
        Test de creacion de seguimientos + fecha_cierre invalida
        Fecha inválida ya que es previa al comienzo

        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "fecha_cierre": "12/12/2020",
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
            ],
            "materias": [self.materia.pk],
        }
        self.client.post(url, data, format="json")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Segundo Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "fecha_cierre": "12/12/2020",
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
            ],
            "materias": [self.materia.pk],
        }
        self.client.post(url, data, format="json")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Tercer Seguimiento2",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "fecha_cierre": "12/12/2020",
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
            ],
            "materias": [self.materia.pk],
        }
        self.client.post(url, data, format="json")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Cuarto Seguimiento3",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "fecha_cierre": "12/12/2020",
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
            ],
            "materias": [self.materia.pk],
        }
        response = self.client.post(url, data, format="json")
        data = {
            "en_progreso": False,
        }
        response = self.client.patch(
            f"/api/seguimientos/{response.data['id']}/status/",
            data,
            format="json",
        )
        response = self.client.get(
            "/api/seguimientos/list/?cerrado=1", format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)

    def test_edit_seguimiento_descripcion_nombre(self):
        """
        Test de edicion de seguimiento
        Valido ya que se puede editar
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "fecha_cierre": "12/12/2020",
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
            ],
            "materias": [self.materia.pk],
        }
        response = self.client.post(url, data, format="json")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento ###",
            "descripcion": "La descripcion",
        }

        response = self.client.patch(
            f"/api/seguimientos/{response.data['id']}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], str(data["nombre"]).upper())
        self.assertEqual(response.data["descripcion"], data["descripcion"])

    def test_edit_seguimiento_all_fields(self):
        """
        Test de edicion de seguimiento
        Editable:
            fecha_cierre
            nombre
            descripción
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "fecha_cierre": "12/12/2020",
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
            ],
            "materias": [self.materia.pk],
        }

        response = self.client.post(url, data, format="json")

        data = {
            "nombre": "Primer Seguimiento ###",
            "descripcion": "La descripcion",
        }

        response = self.client.patch(
            f"/api/seguimientos/{response.data['id']}/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], data["nombre"].upper())
        self.assertEqual(response.data["descripcion"], data["descripcion"])

    def test_edit_seguimiento_integrantes_cannot_erase_encargado(self):
        """
        Test de edicion de integrantes validando que no se pueda borrar al encargado
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "fecha_cierre": "12/12/2020",
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
            ],
            "materias": [self.materia.pk],
        }

        response = self.client.post(url, data, format="json")

        data = [
            {
                "seguimiento": response.data["id"],
                "usuario": self.user_docente.pk,
                "rol": self.rol_profesor.pk,
            },
        ]

        response = self.client.patch(
            f"/api/seguimientos/{response.data['id']}/integrantes/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_seguimiento_integrantes_valid(self):
        """
        Test de edicion de integrantes 
        esto es valido, se agrega un docente
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "fecha_cierre": "12/12/2020",
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
            ],
            "materias": [self.materia.pk],
        }

        response = self.client.post(url, data, format="json")

        data = [
            {
                "seguimiento": response.data["id"],
                "usuario": self.user_docente.pk,
                "rol": self.rol_profesor.pk,
            },
            {
                "id": response.data["integrantes"][0]["id"],
                "seguimiento": response.data["id"],
                "usuario": self.user.pk,
                "rol": self.rol_pedagogo.pk,
            },
        ]

        response = self.client.patch(
            f"/api/seguimientos/{response.data['id']}/integrantes/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_seguimiento_con_integrantes(self):
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
            ],
            "fecha_cierre": "12/12/2020",
            "materias": [self.materia.pk],
        }

        response = self.client.post(url, data, format="json")

        response = self.client.get(
            f"/api/seguimientos/{response.data['id']}/", format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], "PRIMER SEGUIMIENTO")

    def test_seguimiento_unique_positive(self):
        """
        Test de verificacion de seguimiento unico
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
            ],
            "fecha_cierre": "12/12/2020",
            "materias": [self.materia.pk],
        }

        response = self.client.post(url, data, format="json")
        url = reverse("seguimiento-unique")
        data = {
            "nombre": "Primer Seguimiento",
        }
        response = self.client.post(
            "/api/seguimientos/unique/", data, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_seguimiento_unique_negative(self):
        """
        Test de verificacion de seguimiento unico
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
            ],
            "fecha_cierre": "12/12/2020",
            "materias": [self.materia.pk],
        }

        response = self.client.post(url, data, format="json")
        url = reverse("seguimiento-unique")
        data = {
            "nombre": "Primer Seguimiento 2",
        }
        response = self.client.post(
            "/api/seguimientos/unique/", data, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_integrantes(self):
        """
        Test de listado de integrantes 
        se listan los integrantes del seguimiento
        """
        url = reverse("seguimiento-create")
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "nombre": "Primer Seguimiento",
            "descripcion": "La gran descripción de este seguimiento",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
            "fecha_cierre": "12/12/2020",
            "integrantes": [
                {"usuario": self.user.pk, "rol": self.rol_pedagogo.pk},
                {"usuario": self.user_docente.pk, "rol": self.rol_profesor.pk},
            ],
            "materias": [self.materia.pk],
        }

        response = self.client.post(url, data, format="json")

        response = self.client.get(
            f"/api/seguimientos/{response.data['id']}/integrantes/list/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data), ReturnList)

    def test_rol_seguimiento_view(self):
        url = f"/api/seguimientos/rol/{self.rol_pedagogo.pk}/"

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], "Encargado de Seguimiento")

    def test_rol_seguimiento_view_invalid(self):
        url = "/api/seguimientos/rol/900/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rol_seguimiento_list(self):
        url = "/api/seguimientos/rol/list/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SolicitudSeguimientoTest(APITestCase):
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
        cls.group_docente.permissions.add(
            *Permission.objects.values_list("id", flat=True)
        )
        cls.institucion = Institucion.objects.create(
            nombre="MIT", identificador="1234"
        )
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
        cls.rol_tutor = RolSeguimiento.objects.create(nombre="Tutor")

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
        cls.anio2 = Anio.objects.create(
            **{"nombre": "2do Año", "carrera_id": cls.carrera.pk}
        )
        cls.curso = Curso.objects.create(**{"nombre": "1A", "anio": cls.anio})
        cls.curso2 = Curso.objects.create(
            **{"nombre": "2A", "anio": cls.anio2}
        )

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

        cls.materia2 = Materia.objects.create(
            **{"nombre": "Análisis Matemático 2", "anio_id": cls.anio.pk}
        )

        cls.materia3 = Materia.objects.create(
            **{"nombre": "Análisis Matemático 3", "anio_id": cls.anio.pk}
        )

        cls.evaluacion1 = Evaluacion.objects.create(
            **{
                "anio_lectivo": cls.anio_lectivo,
                "materia": cls.materia,
                "ponderacion": 0.5,
                "nombre": "Primera",
            }
        )
        cls.evaluacion2 = Evaluacion.objects.create(
            **{
                "anio_lectivo": cls.anio_lectivo,
                "materia": cls.materia,
                "ponderacion": 0.3,
                "nombre": "Segunda",
            }
        )
        cls.evaluacion3 = Evaluacion.objects.create(
            **{
                "anio_lectivo": cls.anio_lectivo,
                "materia": cls.materia,
                "ponderacion": 0.2,
                "nombre": "Tercera",
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
        cls.alumno_other = Alumno.objects.create(
            dni=3,
            nombre="Alumno3",
            apellido="Alume3",
            institucion=cls.institucion,
        )
        cls.alumno_curso3 = AlumnoCurso.objects.create(
            alumno=cls.alumno_other,
            curso=cls.curso2,
            anio_lectivo=cls.anio_lectivo,
        )

    def setUp(self):
        """
            Fuerzo la autenticacion en cada corrida
        """
        self.client.force_authenticate(user=self.user)
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_create_solicitud_seguimiento(self):
        """
        Test de creacion de solicitud de seguimientos
        """
        url = reverse("solicitudes-create")
        data = {
            "motivo_solicitud": "Motivo muy justificado",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SolicitudSeguimiento.objects.count(), 1)
        self.assertEqual(
            response.data["estado"][0]["estado_solicitud"], "Pendiente"
        )
        self.assertEqual(
            SolicitudSeguimiento.objects.get().motivo_solicitud,
            "Motivo muy justificado",
        )

    def test_create_solicitud_seguimiento_alum_invalidos(self):
        """
        Test de creacion de solicitud de seguimientos 
        con alumnos invalidos
        """
        url = reverse("solicitudes-create")
        data = {
            "motivo_solicitud": "Motivo muy justificado",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso3.pk],
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(SolicitudSeguimiento.objects.count(), 0)

    def test_create_solicitud_seguimiento_motivo_invalidos(self):
        """
        Test de creacion de solicitud de seguimientos 
        con motivo vacio
        """
        url = reverse("solicitudes-create")
        data = {
            "motivo_solicitud": "",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(SolicitudSeguimiento.objects.count(), 0)

    def test_edit_solicitud_seguimiento(self):
        """
        Test de edicion de solicitud de seguimiento
        """
        sol = SolicitudSeguimiento.objects.create(
            motivo_solicitud="Motivo de solicitud", creador=self.user
        )
        sol.alumnos.add(*[self.alumno_curso1.pk, self.alumno_curso2.pk])
        sol.save()
        estado = EstadoSolicitudSeguimiento.objects.filter(
            nombre="Pendiente"
        ).first()
        FechaEstadoSolicitudSeguimiento.objects.create(
            solicitud=sol, estado_solicitud=estado
        )
        url = f"/api/seguimientos/solicitudes/{sol.pk}/"
        data = {
            "motivo_solicitud": "Motivo de solicitud 2",
        }

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(SolicitudSeguimiento.objects.count(), 1)
        self.assertEqual(
            SolicitudSeguimiento.objects.get(pk=sol.pk).motivo_solicitud,
            "Motivo de solicitud 2",
        )

    def test_edit_solicitud_seguimiento_motivo_invalido(self):
        """
        Test de edicion de solicitud de seguimiento con motivos invalidos
        """
        sol = SolicitudSeguimiento.objects.create(
            motivo_solicitud="Motivo de solicitud", creador=self.user
        )
        sol.alumnos.add(*[self.alumno_curso1.pk, self.alumno_curso2.pk])
        sol.save()
        estado = EstadoSolicitudSeguimiento.objects.filter(
            nombre="Pendiente"
        ).first()
        FechaEstadoSolicitudSeguimiento.objects.create(
            solicitud=sol, estado_solicitud=estado
        )
        url = f"/api/seguimientos/solicitudes/{sol.pk}/"
        data = {"motivo_solicitud": ""}

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(SolicitudSeguimiento.objects.count(), 1)
        self.assertEqual(
            SolicitudSeguimiento.objects.get(pk=sol.pk).motivo_solicitud,
            "Motivo de solicitud",
        )

    def test_edit_solicitud_status_valid(self):
        """
        Test de edicion de solicitud de seguimiento con estado valido
        """
        sol = SolicitudSeguimiento.objects.create(
            motivo_solicitud="Motivo de solicitud", creador=self.user
        )
        sol.alumnos.add(*[self.alumno_curso1.pk, self.alumno_curso2.pk])
        sol.save()
        estado = EstadoSolicitudSeguimiento.objects.filter(
            nombre="Pendiente"
        ).first()
        FechaEstadoSolicitudSeguimiento.objects.create(
            solicitud=sol, estado_solicitud=estado
        )
        url = "/api/seguimientos/solicitudes/{}/status/".format(sol.pk)
        data = {"estado": "Aceptada"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_solicitud_status_invalid(self):
        """
        Test de edicion de solicitud de seguimiento con estado invalido
        """
        sol = SolicitudSeguimiento.objects.create(
            motivo_solicitud="Motivo de solicitud", creador=self.user
        )
        sol.alumnos.add(*[self.alumno_curso1.pk, self.alumno_curso2.pk])
        sol.save()
        estado = EstadoSolicitudSeguimiento.objects.filter(
            nombre="Pendiente"
        ).first()
        fecha = FechaEstadoSolicitudSeguimiento.objects.create(
            solicitud=sol, estado_solicitud=estado
        )
        fecha.save()
        url = "/api/seguimientos/solicitudes/{}/status/".format(sol.pk)
        data = {"estado": "Aprobada"}
        # import pdb

        # pdb.set_trace()
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_solicitud_status_invalid_empty(self):
        """
        Test de edicion de solicitud de seguimiento con estado invalido
        """
        sol = SolicitudSeguimiento.objects.create(
            motivo_solicitud="Motivo de solicitud", creador=self.user
        )
        sol.alumnos.add(*[self.alumno_curso1.pk, self.alumno_curso2.pk])
        sol.save()
        estado = EstadoSolicitudSeguimiento.objects.filter(
            nombre="Pendiente"
        ).first()
        FechaEstadoSolicitudSeguimiento.objects.create(
            solicitud=sol, estado_solicitud=estado
        )
        url = f"/api/seguimientos/solicitudes/{sol.pk}/status/"
        data = {"estado": ""}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_solicitud_status_invalid_finished(self):
        """
        Test de edicion de solicitud de seguimiento que ya termino
        Osea esta rechazado o aceptada, no se vuelve de eso
        """
        sol = SolicitudSeguimiento.objects.create(
            motivo_solicitud="Motivo de solicitud", creador=self.user
        )
        sol.alumnos.add(*[self.alumno_curso1.pk, self.alumno_curso2.pk])
        sol.save()
        estado = EstadoSolicitudSeguimiento.objects.filter(
            nombre="Rechazada"
        ).first()
        FechaEstadoSolicitudSeguimiento.objects.create(
            solicitud=sol, estado_solicitud=estado
        )
        url = f"/api/seguimientos/solicitudes/{sol.pk}/status/"
        data = {"estado": "Pendiente"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_solicitud(self):
        """
        Delete solicitud
        """
        sol = SolicitudSeguimiento.objects.create(
            motivo_solicitud="Motivo de solicitud", creador=self.user
        )
        sol.alumnos.add(*[self.alumno_curso1.pk, self.alumno_curso2.pk])
        sol.save()
        estado = EstadoSolicitudSeguimiento.objects.filter(
            nombre="Rechazada"
        ).first()
        FechaEstadoSolicitudSeguimiento.objects.create(
            solicitud=sol, estado_solicitud=estado
        )
        url = f"/api/seguimientos/solicitudes/{sol.pk}/"
        response = self.client.delete(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(SolicitudSeguimiento.objects.count(), 0)

    def test_delete_solicitud_invalid(self):
        """
        Delete solicitud invalida, debido a que no es el dueño
        """
        sol = SolicitudSeguimiento.objects.create(
            motivo_solicitud="Motivo de solicitud", creador=self.user_docente
        )
        sol.alumnos.add(*[self.alumno_curso1.pk, self.alumno_curso2.pk])
        sol.save()
        estado = EstadoSolicitudSeguimiento.objects.filter(
            nombre="Rechazada"
        ).first()
        FechaEstadoSolicitudSeguimiento.objects.create(
            solicitud=sol, estado_solicitud=estado
        )
        url = f"/api/seguimientos/solicitudes/{sol.pk}/"
        response = self.client.delete(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(SolicitudSeguimiento.objects.count(), 1)

    def test_list_solicitudes(self):
        """
        Test de listado solicitudes 
        """
        url = reverse("solicitudes-create")
        data = {
            "motivo_solicitud": "Motivo muy justificado",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
        }
        for i in range(4):
            self.client.post(url, data, format="json")

        response = self.client.get(
            "/api/seguimientos/solicitudes/list/", format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data["results"]), ReturnList)
        self.assertEqual(len(response.data["results"]), 4)

    def test_list_solicitudes_otro(self):
        """
        Test de listado solicitudes ajenas, deberia listar vacío
        """
        url = reverse("solicitudes-create")
        data = {
            "motivo_solicitud": "Motivo muy justificado",
            "alumnos": [self.alumno_curso1.pk, self.alumno_curso2.pk],
        }
        for i in range(4):
            self.client.post(url, data, format="json")
        self.client.force_authenticate(user=self.user_docente)
        response = self.client.get(
            "/api/seguimientos/solicitudes/list/", format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data["results"]), ReturnList)
        self.assertEqual(len(response.data["results"]), 0)
