from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from users.models import User, Group
from django.contrib.auth.models import Permission
from instituciones.models import Institucion
from django.urls import reverse
from rest_framework import status


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
        cls.user = User.objects.create_user(
            "juan@juan.com", password="juan123", groups=cls.group
        )

    def setUp(self):
        """
            Fuerzo la autenticacion en cada corrida
        """
        self.client.force_authenticate(user=self.user)

    def test_create_institucion(self):
        """
        Test de creacion de instituciones
        """
        url = reverse("institucion-create")
        data = {"nombre": "US Federal Reserve", "identificador": "asdfwwe"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Institucion.objects.count(), 1)
        self.assertEqual(
            Institucion.objects.get().nombre, "US FEDERAL RESERVE"
        )

    def test_view_institucion(self):
        """
        Test de creacion de instituciones
        """
        inst = Institucion.objects.create(
            nombre="Hoover Institution", identificador="1234"
        )
        inst.save()
        id_inst = inst.pk
        response = self.client.get(
            "/api/institucion/{}/".format(id_inst), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], "HOOVER INSTITUTION")

    def test_edit_institucion(self):
        """
        Test de edicion de instituciones
        """
        data = {
            "nombre": "Lenin Academy",
            "direccion": "Kaliningrad, 777",
            "pais": "USSR",
            "identificador": "1234f",
        }
        inst = Institucion.objects.create(**data)
        inst.save()
        id_inst = inst.pk
        response = self.client.patch(
            "/api/institucion/{}/".format(id_inst),
            {"pais": "Russia"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Institucion.objects.get(pk=id_inst).pais, "Russia")

    def test_invalid_edit_institucion(self):
        """
        Test de edicion no permitida de instituciones
        """
        data = {
            "nombre": "Lenin Academy",
            "direccion": "Kaliningrad, 777",
            "pais": "USSR",
            "identificador": "123asdf4",
        }
        inst = Institucion.objects.create(**data)
        inst.save()
        id_inst = inst.pk
        response = self.client.patch(
            "/api/institucion/{}/".format(id_inst),
            {"nombre": ""},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_institucion(self):
        """
        Test de eliminacion de instituciones
        """
        data = {
            "nombre": "Lenin Academy",
            "direccion": "Kaliningrad, 777",
            "pais": "USSR",
            "identificador": "asdfjasdf",
        }
        inst = Institucion.objects.create(**data)
        inst.save()
        id_inst = inst.pk
        response = self.client.delete(
            "/api/institucion/{}/".format(id_inst), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            "/api/institucion/{}/".format(id_inst), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_indepotencia_status_institucion(self):
        """
        Test de edicion de indempotencia en el cambio de estado
        """
        data = {
            "nombre": "Lenin Academy",
            "direccion": "Kaliningrad, 777",
            "pais": "USSR",
            "identificador": "asdhf",
        }
        inst = Institucion.objects.create(**data)
        inst.save()
        id_inst = inst.pk
        response = self.client.patch(
            "/api/institucion/{}/status/".format(id_inst),
            {"activa": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Institucion.objects.get(pk=id_inst).activa)

    def test_edit_status_institucion(self):
        """
        Test de edicion de estado
        """
        data = {
            "nombre": "Lenin Academy",
            "direccion": "Kaliningrad, 777",
            "pais": "USSR",
            "identificador": "hfyya",
        }
        inst = Institucion.objects.create(**data)
        inst.save()
        id_inst = inst.pk
        response = self.client.patch(
            "/api/institucion/{}/status/".format(id_inst),
            {"activa": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Institucion.objects.get(pk=id_inst).activa)
