from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from users.models import User, Group
from instituciones.models import Institucion
from django.contrib.auth.models import Permission
from curricula.models import (
    Carrera,
    AnioLectivo,
    Anio,
    Curso,
    Materia,
    Evaluacion,
)
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
        cls.institucion = Institucion.objects.create(
            nombre="MIT", identificador="1234"
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
        cls.anio_lectivo = AnioLectivo.objects.create(
            **{
                "nombre": "2020/2021",
                "fecha_desde": "2020-12-12",
                "fecha_hasta": "2021-12-12",
                "institucion": cls.institucion,
            }
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

    def test_create_and_get_materia(self):
        """
        Test de creacion de materia
        """
        url = reverse("materia-create")
        data = {
            "nombre": "Análisis Matemático",
            "anio": self.anio.pk,
        }

        response = self.client.post(url, data, format="json")
        id_materia = response.data["id"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Materia.objects.count(), 1)
        self.assertEqual(Materia.objects.get().nombre, "ANÁLISIS MATEMÁTICO")
        response = self.client.get("/api/materia/{}/".format(id_materia))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_materia(self):
        """
        Test de creacion de materia
        """
        url = reverse("materia-create")
        data = {
            "nombre": "Análisis Matemático",
            "anio": self.anio.pk,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_materia = response.data["id"]
        self.assertEqual(Materia.objects.count(), 1)

        data = {
            "nombre": "Análisis Matemático 1",
            "color": "verde-claro",
        }

        response = self.client.patch(
            "/api/materia/{}/".format(id_materia), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Materia.objects.count(), 1)
        self.assertEqual(Materia.objects.get().nombre, "ANÁLISIS MATEMÁTICO 1")

    def test_delete_materia(self):
        """
        Test de creacion de materia
        """
        url = reverse("materia-create")
        data = {
            "nombre": "Análisis Matemático",
            "anio": self.anio.pk,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_materia = response.data["id"]
        self.assertEqual(Materia.objects.count(), 1)
        response = self.client.delete("/api/materia/{}/".format(id_materia))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Materia.objects.count(), 0)

    def test_view_delete_materia_de_otra_institucion(self):
        """
        Test para checkear de que no es posible ver o eliminar \
        una materia de otra Institucion
        """
        institucion = Institucion.objects.create(
            nombre="NYU", identificador="123456"
        )
        institucion.save()
        carrera = Carrera.objects.create(
            **{
                "nombre": "Ingenieria en Creatividad",
                "institucion_id": institucion.pk,
            }
        )
        carrera.save()
        anio = Anio.objects.create(
            **{"nombre": "Primer Año NYU", "carrera_id": carrera.pk}
        )
        anio.save()
        materia = Materia.objects.create(
            **{"nombre": "Análisis Matemático", "anio_id": anio.pk}
        )
        materia.save()
        # Ver
        response = self.client.get("/api/materia/{}/".format(materia.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Borrar
        response = self.client.delete("/api/materia/{}/".format(materia.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_evaluaciones_success(self):
        """
        Test de creacion de evaluaciones
        """
        materia = Materia.objects.create(
            **{"nombre": "Análisis Matemático", "anio_id": self.anio.pk}
        )
        materia.save()
        url = reverse("evaluacion-create")
        data = [
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 0.5,
            },
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 0.5,
            },
        ]

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Evaluacion.objects.count(), 2)

    def test_list_evaluaciones(self):
        """
        Test de listado de evaluaciones
        """
        materia = Materia.objects.create(
            **{"nombre": "Análisis Matemático", "anio_id": self.anio.pk}
        )
        materia.save()
        url = reverse("evaluacion-create")
        data = [
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 0.5,
            },
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 0.5,
            },
        ]

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(
            "/api/materia/{}/evaluacion/list/".format(materia.pk),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data), ReturnList)
        self.assertEqual(len(response.data), 2)

    def test_delete_evaluaciones(self):
        """
        Test de listado de evaluaciones
        """
        materia = Materia.objects.create(
            **{"nombre": "Análisis Matemático", "anio_id": self.anio.pk}
        )
        materia.save()
        url = reverse("evaluacion-create")
        data = [
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 0.5,
            },
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 0.5,
            },
        ]

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {
            "anio_lectivo": self.anio_lectivo.pk,
            "materia": materia.pk,
        }
        response = self.client.delete(
            "/api/evaluacion/", data=data, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Evaluacion.objects.count(), 0)

    def test_edit_in_bulk_evaluaciones(self):
        """
        Test de listado de evaluaciones
        """
        materia = Materia.objects.create(
            **{"nombre": "Análisis Matemático", "anio_id": self.anio.pk}
        )
        materia.save()
        url = reverse("evaluacion-create")
        data = [
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 0.5,
                "nombre": "nombre1",
            },
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 0.3,
                "nombre": "nombre2",
            },
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 0.2,
                "nombre": "nombre3",
            },
        ]
        response = self.client.post(url, data, format="json")

        response = self.client.get(
            "/api/materia/{}/evaluacion/list/?anio_lectivo={}".format(
                materia.pk, self.anio_lectivo.pk
            ),
        )
        data = []
        data.append(response.data[0])
        data[0]["anio_lectivo"] = self.anio_lectivo.pk
        del data[0]["nombre"]
        data[0]["materia"] = materia.pk
        data.append(
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 0.5,
                "nombre": "nombre4",
            }
        )
        response = self.client.put(
            "/api/evaluacion/", data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            "/api/materia/{}/evaluacion/list/?anio_lectivo={}".format(
                materia.pk, self.anio_lectivo.pk
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data), ReturnList)
        self.assertEqual(len(response.data), 2)

    def test_create_evaluaciones_ponderacion_erronea(self):
        """
        Test de validacion sobre ponderacion en la creacion de evaluaciones
        """
        materia = Materia.objects.create(
            **{"nombre": "Análisis Matemático", "anio_id": self.anio.pk}
        )
        materia.save()
        url = reverse("evaluacion-create")
        data = [
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 1,
            },
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 0,
            },
        ]

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Evaluacion.objects.count(), 0)
        data = [
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 0.3,
            },
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 0.2,
            },
        ]

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Evaluacion.objects.count(), 0)
        data = [
            {"anio_lectivo": self.anio_lectivo.pk, "materia": materia.pk},
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 0.2,
            },
        ]

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Evaluacion.objects.count(), 0)

    def test_create_evaluaciones_con_pk_erroneas(self):
        """
        Test de validacion sobre ponderacion en la creacion de evaluaciones
        """
        materia = Materia.objects.create(
            **{"nombre": "Análisis Matemático", "anio_id": self.anio.pk}
        )
        materia.save()
        materia2 = Materia.objects.create(
            **{"nombre": "Análisis Matemático 2", "anio_id": self.anio.pk}
        )
        materia2.save()
        url = reverse("evaluacion-create")
        data = [
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia2.pk,
                "ponderacion": 1,
            },
            {
                "anio_lectivo": self.anio_lectivo.pk,
                "materia": materia.pk,
                "ponderacion": 0,
            },
        ]

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Evaluacion.objects.count(), 0)


class AnioCursoTest(APITestCase):
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
        cls.group.save()
        cls.institucion = Institucion.objects.create(
            nombre="MIT", identificador="1234"
        )
        cls.institucion.save()
        cls.carrera = Carrera.objects.create(
            **{
                "nombre": "Ingenieria en Creatividad",
                "institucion_id": cls.institucion.pk,
            }
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

    def test_create_anio(self):
        """
        Test de creacion de Años
        """
        url = reverse("anio-create")
        data = {
            "nombre": "Primer Año",
            "carrera": self.carrera.pk,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Anio.objects.count(), 1)
        self.assertEqual(Anio.objects.get().nombre, "PRIMER AÑO")

    def test_create_anio_con_cursos(self):
        """
        Test de creacion de Años mas Cursos
        """
        url = reverse("anio-create")
        data = {
            "nombre": "Primer Año",
            "carrera": self.carrera.pk,
            "cursos": [{"nombre": "1A"}, {"nombre": "2A"}],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Anio.objects.count(), 1)
        self.assertEqual(Curso.objects.count(), 2)

    def test_edit_anio_complete(self):
        """
        Test de edicion de Años
        """
        url = reverse("anio-create")
        data = {
            "nombre": "Primer Año",
            "carrera": self.carrera.pk,
        }
        response = self.client.post(url, data, format="json")
        id_anio = response.data["id"]
        data = {
            "nombre": "Primer Añejo",
            "descripcion": "El primero",
            "color": "rojo-fuerte",
        }

        response = self.client.patch(
            "/api/anio/{}/".format(id_anio), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Anio.objects.get().nombre, "PRIMER AÑEJO")

    def test_edit_anio_invalid_name(self):
        """
        Test de edicion de Fallida
        """
        url = reverse("anio-create")
        data = {
            "nombre": "Primer Año",
            "carrera": self.carrera.pk,
        }
        response = self.client.post(url, data, format="json")
        id_anio = response.data["id"]
        data = {
            "nombre": "",
            "descripcion": "El primero",
            "color": "rojo-fuerte",
        }

        response = self.client.patch(
            "/api/anio/{}/".format(id_anio), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anio_curso_view_de_otra_institucion(self):
        """
        Test para checkear de que no es posible ver un anio de otra Institucion
        """
        institucion = Institucion.objects.create(
            nombre="NYU", identificador="1236544"
        )
        institucion.save()
        carrera = Carrera.objects.create(
            **{
                "nombre": "Ingenieria en Creatividad",
                "institucion_id": institucion.pk,
            }
        )
        carrera.save()
        anio = Anio.objects.create(
            **{"nombre": "Primer Año NYU", "carrera_id": carrera.pk,}
        )
        anio.save()
        curso = Curso.objects.create(nombre="1A", anio_id=anio.pk)
        curso.save()
        response = self.client.get("/api/anio/{}/".format(anio.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get(
            "/api/curso/{}/".format(curso.pk), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_edit_curso_de_anio(self):
        """
        Test de edicion de un curso
        """
        url = reverse("anio-create")
        data = {
            "nombre": "Primer Año",
            "carrera": self.carrera.pk,
            "cursos": [{"nombre": "1A"}, {"nombre": "2A"}],
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Anio.objects.count(), 1)

        self.assertEqual(Curso.objects.count(), 2)
        for curso in Curso.objects.all():
            response = self.client.get(
                "/api/curso/{}/".format(curso.pk), format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["nombre"], curso.nombre)
        data = {
            "nombre": "1AA",
        }
        response = self.client.patch(
            "/api/curso/{}/".format(curso.pk), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], "1AA")

    def test_delete_anio_con_cursos_gives_400(self):
        """
        Test de borrado de anio y cascade a cursos
        """
        url = reverse("anio-create")
        data = {
            "nombre": "Primer Año",
            "carrera": self.carrera.pk,
            "cursos": [{"nombre": "1A"}, {"nombre": "2A",}],
        }
        response = self.client.post(url, data, format="json")
        anio_id = response.data["id"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Anio.objects.count(), 1)

        self.assertEqual(Curso.objects.count(), 2)
        response = self.client.delete(
            "/api/anio/{}/".format(anio_id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for curso in Curso.objects.all():
            response = self.client.get(
                "/api/curso/{}/".format(curso.pk), format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_curso_de_anio(self):
        """
        Test de borrado de anio y cascade a cursos
        """
        url = reverse("anio-create")
        data = {
            "nombre": "Primer Año",
            "carrera": self.carrera.pk,
            "cursos": [{"nombre": "1A"}, {"nombre": "2A"}],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Anio.objects.count(), 1)
        self.assertEqual(Curso.objects.count(), 2)
        curso = Curso.objects.first()
        response = self.client.delete(
            "/api/curso/{}/".format(curso.pk), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            "/api/curso/{}/".format(curso.pk), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CarreraTests(APITestCase):
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
        cls.group.save()
        cls.institucion = Institucion.objects.create(
            nombre="MIT", identificador="1234"
        )
        cls.institucion.save()
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

    def test_create_carrera(self):
        """
        Test de creacion de carreras
        """
        url = reverse("carrera-create")
        data = {"nombre": "Ingenieria en Creatividad"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Carrera.objects.count(), 1)
        self.assertEqual(
            Carrera.objects.get().nombre, "INGENIERIA EN CREATIVIDAD"
        )
        self.assertEqual(
            Carrera.objects.get().institucion.pk, self.institucion.pk
        )

    def test_name_required_create_carrera(self):
        """
        Test de creacion de carreras
        """
        url = reverse("carrera-create")
        data = {"color": "#000000"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_carrera(self):
        """
        Test de creacion de instituciones
        """
        carrera = Carrera.objects.create(
            nombre="Ingenieria en Baile", institucion=self.institucion
        )
        carrera.save()
        id_carrera = carrera.pk
        response = self.client.get(
            "/api/carrera/{}/".format(id_carrera), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], "INGENIERIA EN BAILE")

    def test_edit_carrera(self):
        """
        Test de edicion de instituciones
        """
        data = {
            "nombre": "Ingenieria en Creatividad",
            "color": "#010101",
            "descripcion": "GDP BOOSTER",
            "institucion": self.institucion,
        }
        carrera = Carrera.objects.create(**data)
        carrera.save()
        id_carrera = carrera.pk
        response = self.client.patch(
            "/api/carrera/{}/".format(id_carrera),
            {"color": "#00000"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Carrera.objects.get(pk=id_carrera).color, "#00000")

    def test_invalid_edit_carrera(self):
        """
        Test de edicion no permitida de instituciones
        """
        data = {
            "nombre": "Ingenieria en Creatividad",
            "color": "#010101",
            "descripcion": "GDP BOOSTER",
            "institucion": self.institucion,
        }
        inst = Carrera.objects.create(**data)
        inst.save()
        id_carrera = inst.pk
        response = self.client.patch(
            "/api/carrera/{}/".format(id_carrera),
            {"nombre": ""},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_carrera(self):
        """
        Test de eliminacion de carreras
        """
        data = {
            "nombre": "Ingenieria en Creatividad",
            "color": "#010101",
            "descripcion": "GDP BOOSTER",
            "institucion": self.institucion,
        }
        inst = Carrera.objects.create(**data)
        inst.save()
        id_carrera = inst.pk
        response = self.client.delete(
            "/api/carrera/{}/".format(id_carrera), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            "/api/carrera/{}/".format(id_carrera), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_carrera(self):
        """
        Test de listado de carreras
        """
        response = self.client.get("/api/carrera/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data), ReturnList)


class AnioLectivoTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup de User y permisos para poder ejecutar todas las acciones
        """
        cls.client = APIClient()
        cls.group_admin = Group.objects.create(name="Admin1")
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can add anio lectivo")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can change anio lectivo")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can delete anio lectivo")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Puede listar años lectivos")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can view anio lectivo")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Puede ver el año lectivo actual")
        )
        cls.group_admin.save()

        cls.group_docente = Group.objects.create(name="Docente1")
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Puede listar años lectivos")
        )
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Can view anio lectivo")
        )
        cls.group_docente.save()

        cls.institucion_1 = Institucion.objects.create(
            nombre="Institucion_1", identificador="1234"
        )
        cls.institucion_2 = Institucion.objects.create(
            nombre="Institucion_2", identificador="1dg234"
        )

        cls.user_admin_1 = User.objects.create_user(
            "juan1@juan.com",
            password="password",
            groups=cls.group_admin,
            institucion=cls.institucion_1,
        )
        cls.user_docente_1 = User.objects.create_user(
            "juan2@juan.com",
            password="password",
            groups=cls.group_docente,
            institucion=cls.institucion_1,
        )

        cls.user_admin_2 = User.objects.create_user(
            "juan3@juan.com",
            password="password",
            groups=cls.group_admin,
            institucion=cls.institucion_2,
        )
        cls.user_docente_2 = User.objects.create_user(
            "juan4@juan.com",
            password="password",
            groups=cls.group_docente,
            institucion=cls.institucion_2,
        )

        cls.anio_lectivo_institucion_1 = AnioLectivo.objects.create(
            **{
                "nombre": "2020",
                "fecha_desde": "2020-01-01",
                "fecha_hasta": "2020-12-31",
                "institucion": cls.institucion_1,
            }
        )
        cls.anio_lectivo_institucion_1.save()

        cls.anio_lectivo_institucion_2 = AnioLectivo.objects.create(
            **{
                "nombre": "2019",
                "fecha_desde": "2019-01-01",
                "fecha_hasta": "2019-12-31",
                "institucion": cls.institucion_2,
            }
        )
        cls.anio_lectivo_institucion_2.save()

        cls.anio_lectivo2_institucion_1 = AnioLectivo.objects.create(
            **{
                "nombre": "1998",
                "fecha_desde": "1998-01-01",
                "fecha_hasta": "1998-12-31",
                "institucion": cls.institucion_1,
            }
        )
        cls.anio_lectivo2_institucion_1.save()

        cls.anio_lectivo3_institucion_1 = AnioLectivo.objects.create(
            **{
                "nombre": "2030",
                "fecha_desde": "2030-01-01",
                "fecha_hasta": "2030-12-31",
                "institucion": cls.institucion_1,
            }
        )
        cls.anio_lectivo3_institucion_1.save()

    def test_create_admin(self):
        """
        Test de creacion correcta de anios lectivos por admin
        """
        self.client.force_authenticate(user=self.user_admin_1)
        data = {
            "nombre": "2017",
            "fecha_desde": "01/01/2017",
            "fecha_hasta": "31/12/2017",
        }
        response = self.client.post("/api/anio_lectivo/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {
            "nombre": "2019",
            "fecha_desde": "01/01/2019",
            "fecha_hasta": "31/12/2019",
        }
        response = self.client.post("/api/anio_lectivo/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_docente(self):
        """
        Test de creacion no permitida de anios lectivos por docente
        """
        self.client.force_authenticate(user=self.user_docente_1)
        data = {
            "nombre": "2018",
            "fecha_desde": "01/01/2018",
            "fecha_hasta": "31/12/2018",
        }
        response = self.client.post("/api/anio_lectivo/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_admin_incorrect(self):
        """
        Test de creacion de anios lectivos por admin con datos faltantes
        """
        self.client.force_authenticate(user=self.user_admin_1)
        data1 = {
            "fecha_desde": "01/01/2018",
            "fecha_hasta": "31/12/2018",
        }
        data2 = {
            "nombre": "2018",
            "fecha_hasta": "31/12/2018",
        }
        data3 = {
            "nombre": "2018",
            "fecha_desde": "01/01/2018",
        }
        response1 = self.client.post(
            "/api/anio_lectivo/", data1, format="json"
        )
        response2 = self.client.post(
            "/api/anio_lectivo/", data2, format="json"
        )
        response3 = self.client.post(
            "/api/anio_lectivo/", data3, format="json"
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "nombre": "2020",
            "fecha_desde": "01/01/2056",
            "fecha_hasta": "31/12/2056",
        }
        response = self.client.post("/api/anio_lectivo/", data, format="json")
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_admin_wrong_dates(self):
        """
        Test de creacion de anios lectivos por admin con fechas incorrectas
        """
        self.client.force_authenticate(user=self.user_admin_1)
        data = {
            "nombre": "2018",
            "fecha_desde": "01/01/2019",
            "fecha_hasta": "31/12/2018",
        }
        response = self.client.post("/api/anio_lectivo/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_admin_conficting_dates(self):
        """
        Test de creacion de anios lectivos por admin con fechas conflictivas
        """
        self.client.force_authenticate(user=self.user_admin_1)
        data1 = {
            "nombre": "2020",
            "fecha_desde": "01/02/2020",
            "fecha_hasta": "20/12/2021",
        }
        data2 = {
            "nombre": "2020-1",
            "fecha_desde": "01/01/2019",
            "fecha_hasta": "30/11/2020",
        }
        data3 = {
            "nombre": "2020-2",
            "fecha_desde": "02/01/2019",
            "fecha_hasta": "20/6/2021",
        }
        data4 = {
            "nombre": "2019-1",
            "fecha_desde": "01/01/2019",
            "fecha_hasta": "31/12/2019",
        }
        response1 = self.client.post(
            "/api/anio_lectivo/", data1, format="json"
        )
        response2 = self.client.post(
            "/api/anio_lectivo/", data2, format="json"
        )
        response3 = self.client.post(
            "/api/anio_lectivo/", data3, format="json"
        )
        response4 = self.client.post(
            "/api/anio_lectivo/", data4, format="json"
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response4.status_code, status.HTTP_201_CREATED)

    def test_get(self):
        """
        Test de obtener un anio lectivo
        """
        self.client.force_authenticate(user=self.user_admin_1)

        response1 = self.client.get(
            "/api/anio_lectivo/{}/".format(self.anio_lectivo_institucion_1.pk)
        )
        response2 = self.client.get(
            f"/api/anio_lectivo/{self.anio_lectivo_institucion_2.id}/"
        )
        response3 = self.client.get("/api/anio_lectivo/20000/")

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertDictContainsSubset(
            {"id": self.anio_lectivo_institucion_1.pk}, response1.data
        )
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response3.status_code, status.HTTP_404_NOT_FOUND)

    def test_actual(self):
        """
        Test de obtener un anio lectivo corriente
        """
        self.client.force_authenticate(user=self.user_admin_1)

        response1 = self.client.get("/api/anio_lectivo/actual/")

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertDictContainsSubset(
            {"id": self.anio_lectivo_institucion_1.pk}, response1.data
        )

    def test_destroy_admin(self):
        """
        Test de borrar anios_lectivos por un administrador
        """
        self.client.force_authenticate(user=self.user_admin_1)
        id1 = AnioLectivo.objects.get(nombre="2020").id
        id2 = AnioLectivo.objects.get(nombre="2019").id
        response1 = self.client.delete("/api/anio_lectivo/{}/".format(id1))
        response2 = self.client.delete("/api/anio_lectivo/{}/".format(id2))
        response3 = self.client.delete("/api/anio_lectivo/60/")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response3.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_docente(self):
        """
        Test de borrar anios_lectivos por un docente
        """
        self.client.force_authenticate(user=self.user_docente_1)
        id1 = AnioLectivo.objects.get(nombre="2020").id
        response1 = self.client.delete("/api/anio_lectivo/{}/".format(id1))
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_correct(self):
        """
        Test de listado de anios lectivos
        """
        self.client.force_authenticate(user=self.user_admin_1)
        response = self.client.get("/api/anio_lectivo/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(type(response.data), ReturnList)

    def test_update_admin_correct(self):
        """
        Test de actualizar un anio lectivo por un admin correctamente
        """
        self.client.force_authenticate(user=self.user_admin_1)
        id_anio_lectivo = AnioLectivo.objects.get(nombre="2030").id

        data = {
            "nombre": "1999",
            "fecha_desde": "01/01/1999",
            "fecha_hasta": "31/12/1999",
        }
        response = self.client.patch(
            "/api/anio_lectivo/{}/".format(id_anio_lectivo),
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data1 = {
            "nombre": "2030",
            "fecha_desde": "01/01/2030",
            "fecha_hasta": "31/12/2030",
        }
        response1 = self.client.patch(
            "/api/anio_lectivo/{}/".format(id_anio_lectivo),
            data=data1,
            format="json",
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_admin_wrong_dates_not_passed(self):
        """
        Test de actualizar un anio lectivo por un admin con fechas incorrectas y todavía no empezado
        """
        self.client.force_authenticate(user=self.user_admin_1)
        id_anio_lectivo = AnioLectivo.objects.get(nombre="2030").id

        data = {"fecha_desde": "01/12/2030", "fecha_hasta": "01/01/2030"}
        response = self.client.patch(
            "/api/anio_lectivo/{}/".format(id_anio_lectivo),
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_admin_wrong_dates_started_or_passed(self):
        """
        Test de actualizar un anio lectivo por un admin con fechas incorrectas y empezado o terminado
        """
        self.client.force_authenticate(user=self.user_admin_1)
        id_anio_lectivo = AnioLectivo.objects.get(nombre="1998").id

        data = {"fecha_desde": "01/01/2021", "fecha_hasta": "01/12/2021"}
        response = self.client.patch(
            "/api/anio_lectivo/{}/".format(id_anio_lectivo),
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_admin_conflicting_dates(self):
        """
        Test de actualizar un anio lectivo por un admin con fechas conflictivas con otros anios lectivos
        """
        self.client.force_authenticate(user=self.user_admin_1)
        id_anio_lectivo = AnioLectivo.objects.get(nombre="2030").id

        data = {"fecha_desde": "01/01/2020", "fecha_hasta": "01/12/2020"}
        response = self.client.patch(
            "/api/anio_lectivo/{}/".format(id_anio_lectivo),
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {"fecha_desde": "01/01/2019", "fecha_hasta": "01/12/2019"}
        response = self.client.patch(
            "/api/anio_lectivo/{}/".format(id_anio_lectivo),
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_admin_name_started_or_passed(self):
        """
        Test de actualizar un anio lectivo por un admin modificando su nombre si ha empezado o pasado
        """
        self.client.force_authenticate(user=self.user_admin_1)
        id_anio_lectivo = AnioLectivo.objects.get(nombre="1998").id

        data = {"nombre": "1998-1"}
        response = self.client.patch(
            "/api/anio_lectivo/{}/".format(id_anio_lectivo),
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_admin_other_institucion_or_not_existent(self):
        """
        Test de actualizar un anio lectivo por un admin de otra institucion o no existente
        """
        self.client.force_authenticate(user=self.user_admin_1)
        id_anio_lectivo = AnioLectivo.objects.get(nombre="2019").id

        data = {"nombre": "1998-1"}
        response = self.client.patch(
            "/api/anio_lectivo/{}/".format(id_anio_lectivo),
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.patch(
            "/api/anio_lectivo/60/", data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_docente(self):
        """
        Test de actualizar un anio lectivo por un docente
        """
        self.client.force_authenticate(user=self.user_docente_1)
        id_anio_lectivo = AnioLectivo.objects.get(nombre="1998").id

        data = {"nombre": "1998-1"}
        response = self.client.patch(
            "/api/anio_lectivo/{}/".format(id_anio_lectivo),
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
