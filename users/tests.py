from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from users.models import User, Group
from django.contrib.auth.models import Permission
from instituciones.models import Institucion
import logging


class AuthenticationTests(APITestCase):
    # TODO 1: Testear login fallido, agregar GRUPO!
    def setUp(self):
        """
            Creo el usuario, le doy permisos de creacion de usuarios
            Lo logeo creando el Token 
        """
        self.client = APIClient()
        self.group = Group.objects.create(name="Docente")
        self.group.save()
        self.group.permissions.add(Permission.objects.get(name="Can add user"))
        self.institucion = Institucion.objects.create(
            nombre="SNU", identificador="1234"
        )
        self.user = User.objects.create_user(
            "juan@juan.com",
            password="juan123",
            groups=self.group,
            institucion=self.institucion,
        )

        self.token = Token.objects.create(user=self.user)
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_register_while_logged_in_and_valid_data(self):
        new_user = {
            "email": "pedro@pedro.com",
            "password": "pedrito123",
            "password2": "pedrito123",
            "groups": self.group.id,
        }
        response = self.client.post(
            "/api/users/",
            data=new_user,
            format="json",
            HTTP_AUTHORIZATION="Token " + self.token.key,
        )
        self.assertEqual(response.status_code, 201)

    def test_register_while_logged_in_and_non_matching_passwords(self):
        new_user = {
            "email": "pedro@pedro.com",
            "password": "pedrito123",
            "password2": "a",
            "groups": self.group.id,
        }
        response = self.client.post(
            "/api/users/",
            data=new_user,
            format="json",
            HTTP_AUTHORIZATION="Token " + self.token.key,
        )
        self.assertEqual(response.status_code, 400)

    def test_logout_successful(self):
        response = self.client.get(
            "/api/users/logout/", HTTP_AUTHORIZATION="Token " + self.token.key
        )

        self.assertEqual(response.status_code, 200)

    def test_logout_unauthorized(self):
        response = self.client.get(
            "/api/users/logout/", HTTP_AUTHORIZATION="not_a_token"
        )

        self.assertEqual(response.status_code, 401)


class PermissionsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.group_docente = Group.objects.create(name="Docente")
        self.group_docente.save()
        self.group_docente.permissions.add(
            Permission.objects.get(name="Can add user")
        )
        self.group_otro = Group.objects.create(name="Otro")
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_forbidden_action(self):
        user = User.objects.create_user(
            "juan@juan.com", password="juan123", groups=self.group_otro
        )

        token = Token.objects.create(user=user)
        new_user = {
            "email": "pedro@pedro.com",
            "password": "pedrito123",
            "password2": "pedrito123",
            "groups": self.group_docente.id,
        }
        response = self.client.post(
            "/api/users/",
            data=new_user,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 403)

    def test_permitted_action(self):
        user = User.objects.create_user(
            "juan@juan.com", password="juan123", groups=self.group_docente
        )

        token = Token.objects.create(user=user)
        new_user = {
            "email": "pedro@pedro.com",
            "password": "pedrito123",
            "password2": "pedrito123",
            "groups": self.group_docente.id,
        }
        response = self.client.post(
            "/api/users/",
            data=new_user,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 201)


class UsersTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.group_admin = Group.objects.create(name="Admin1")
        cls.group_admin.save()
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can view group")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can view institucion")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can add user")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can edit other users info")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can change user")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can change status of User")
        )
        cls.group_admin.permissions.add(
            Permission.objects.get(name="Can view user")
        )

        cls.group_docente = Group.objects.create(name="Docente1")
        cls.group_docente.save()
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Can view group")
        )
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Can view institucion")
        )
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Can change user")
        )
        cls.group_docente.permissions.add(
            Permission.objects.get(name="Can view user")
        )

        cls.institucion_1 = Institucion.objects.create(
            nombre="Institucion_1", identificador="1234"
        )
        cls.institucion_2 = Institucion.objects.create(
            nombre="Institucion_2", identificador="12adsf34"
        )

        cls.user_admin_1 = User.objects.create_user(
            "juan1@juan.com",
            password="password",
            groups=cls.group_admin,
            institucion=cls.institucion_1,
        )
        cls.user_admin_1.save()
        cls.user_docente_1 = User.objects.create_user(
            "juan2@juan.com",
            password="password",
            groups=cls.group_docente,
            institucion=cls.institucion_1,
        )
        cls.user_docente_1.save()
        cls.user_docente_3 = User.objects.create_user(
            "juan3@juan.com",
            password="password",
            groups=cls.group_docente,
            institucion=cls.institucion_1,
        )
        cls.user_docente_3.save()

        cls.user_admin_2 = User.objects.create_user(
            "juan4@juan.com",
            password="password",
            groups=cls.group_admin,
            institucion=cls.institucion_2,
        )
        cls.user_admin_2.save()
        cls.user_docente_2 = User.objects.create_user(
            "juan5@juan.com",
            password="password",
            groups=cls.group_docente,
            institucion=cls.institucion_2,
        )
        cls.user_docente_2.save()
        cls.user_docente_4 = User.objects.create_user(
            "juan6@juan.com",
            password="password",
            groups=cls.group_docente,
            institucion=cls.institucion_2,
        )
        cls.user_docente_4.save()

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_create_user_admin_authenticated(self):
        token = Token.objects.create(user=self.user_admin_1)
        new_user = {
            "email": "pedro@pedro.com",
            "password": "pedrito123",
            "password2": "pedrito123",
            "groups": self.group_docente.id,
        }
        response = self.client.post(
            "/api/users/",
            data=new_user,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 201)

    def test_create_user_admin_not_authenticated(self):
        token = Token.objects.create(user=self.user_admin_1)
        new_user = {
            "email": "pedro@pedro.com",
            "password": "pedrito123",
            "password2": "pedrito123",
            "groups": self.group_docente.id,
        }
        response = self.client.post(
            "/api/users/", data=new_user, format="json"
        )

        self.assertEqual(response.status_code, 401)

    def test_create_user_admin_not_email(self):
        token = Token.objects.create(user=self.user_admin_1)
        new_user = {
            "password": "pedrito123",
            "password2": "pedrito123",
            "groups": self.group_docente.id,
        }
        response = self.client.post(
            "/api/users/",
            data=new_user,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 400)

    def test_create_user_admin_not_matching_passwords(self):
        token = Token.objects.create(user=self.user_admin_1)
        new_user = {
            "email": "pedro@pedro.com",
            "password": "pedrito13",
            "password2": "pedrito123",
            "groups": self.group_docente.id,
        }
        response = self.client.post(
            "/api/users/",
            data=new_user,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 400)

    def test_create_user_docente(self):
        token = Token.objects.create(user=self.user_docente_1)
        new_user = {
            "email": "pedro@pedro.com",
            "password": "pedrito13",
            "password2": "pedrito123",
            "groups": self.group_docente.id,
        }
        response = self.client.post(
            "/api/users/",
            data=new_user,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 403)

    def test_list_(self):
        token = Token.objects.create(user=self.user_docente_1)
        response = self.client.get(
            "/api/users/list/", HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(len(response.data), 4)

    def test_destroy_user_docente(self):
        token = Token.objects.create(user=self.user_docente_1)
        response = self.client.delete(
            "/api/users/1/", HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 403)

    def test_destroy_user_admin(self):
        token = Token.objects.create(user=self.user_admin_1)
        response = self.client.delete(
            "/api/users/1/", HTTP_AUTHORIZATION="Token " + token.key,
        )

        self.assertEqual(response.status_code, 403)

    def test_destroy_user_error(self):
        token = Token.objects.create(user=self.user_admin_1)
        response = self.client.delete(
            "/api/users/x/", HTTP_AUTHORIZATION="Token " + token.key,
        )

        self.assertEqual(response.status_code, 404)

    def test_get_user_admin_failed(self):
        token = Token.objects.create(user=self.user_admin_1)
        response = self.client.get(
            "/api/users/14/", HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 404)

    def test_get_user_admin_correct(self):
        token = Token.objects.create(user=self.user_admin_1)
        response = self.client.get(
            f"/api/users/{self.user_docente_1.id}/",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset(
            {"id": self.user_docente_1.id}, response.data
        )

    def test_status_user_admin_correct(self):
        token = Token.objects.create(user=self.user_admin_1)
        estado = {"is_active": "false"}
        response = self.client.patch(
            f"/api/users/{self.user_docente_1.id}/status/",
            data=estado,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 200)

    def test_status_user_admin_incorrect(self):
        token = Token.objects.create(user=self.user_admin_1)
        estado = {"is_active": "false"}
        response = self.client.patch(
            f"/api/users/{self.user_admin_1.id}/status/",
            data=estado,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 400)

    def test_status_user_admin_redundant(self):
        token = Token.objects.create(user=self.user_admin_1)
        estado = {"is_active": "true"}
        response = self.client.patch(
            f"/api/users/{self.user_docente_1.id}/status/",
            data=estado,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 202)

    def test_status_user_admin_bad_request(self):
        token = Token.objects.create(user=self.user_admin_1)
        estado = {"is_active": ""}
        response = self.client.patch(
            f"/api/users/{self.user_docente_1.id}/status/",
            data=estado,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 400)

    def test_status_user_docente(self):
        token = Token.objects.create(user=self.user_docente_1)
        estado = {"is_active": "false"}
        response = self.client.patch(
            "/api/users/13/status/",
            data=estado,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 403)

    def test_status_user_admin_other_institution(self):
        token = Token.objects.create(user=self.user_admin_1)
        estado = {"is_active": "true"}
        response = self.client.patch(
            f"/api/users/{self.user_docente_2.id}/status/",
            data=estado,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 404)

    def test_update_user_admin_not_existing_user(self):
        token = Token.objects.create(user=self.user_admin_1)
        data = {"email": "hola@hola.com"}
        response = self.client.patch(
            "/api/users/200/",
            data=data,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 404)

    def test_update_user_admin_self(self):
        token = Token.objects.create(user=self.user_admin_1)
        data = {"email": "hola@hola.com"}
        response = self.client.patch(
            f"/api/users/{self.user_admin_1.id}/",
            data=data,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 200)

    def test_update_user_admin_other(self):
        token = Token.objects.create(user=self.user_admin_1)
        data = {"email": "hola2@hola.com"}
        response = self.client.patch(
            f"/api/users/{self.user_docente_1.id}/",
            data=data,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 200)

    def test_update_user_admin_other_institucion(self):
        token = Token.objects.create(user=self.user_admin_1)
        data = {"email": "hola3@hola.com"}
        response = self.client.patch(
            f"/api/users/{self.user_docente_4.id}/",
            data=data,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 404)

    def test_update_user_admin_other_not_active(self):
        token = Token.objects.create(user=self.user_admin_1)

        estado = {"is_active": "false"}
        response = self.client.patch(
            f"/api/users/{self.user_docente_3.id}/status/",
            data=estado,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )

        data = {"email": "hola4@hola.com"}
        response = self.client.patch(
            f"/api/users/{self.user_docente_3.id}/",
            data=data,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 400)

    def test_update_user_docente_self(self):
        token = Token.objects.create(user=self.user_docente_1)
        data = {"email": "hola7@hola.com"}
        response = self.client.patch(
            f"/api/users/{self.user_docente_1.id}/",
            data=data,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 200)

    def test_update_user_docente_other(self):
        token = Token.objects.create(user=self.user_docente_1)
        data = {"email": "hola8@hola.com"}
        response = self.client.patch(
            f"/api/users/{self.user_docente_3.id}/",
            data=data,
            format="json",
            HTTP_AUTHORIZATION="Token " + token.key,
        )
        self.assertEqual(response.status_code, 403)

