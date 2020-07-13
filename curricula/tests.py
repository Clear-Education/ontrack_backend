from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from users.models import User, Group
from instituciones.models import Institucion
from django.contrib.auth.models import Permission
from curricula.models import Carrera
from django.urls import reverse
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnList


class InstitucionTests(APITestCase):
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
        cls.institucion = Institucion.objects.create(nombre="MIT")
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
            Carrera.objects.get().nombre, "Ingenieria en Creatividad"
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
        self.assertEqual(response.data["nombre"], "Ingenieria en Baile")

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

