from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from users.models import User, Group
from django.contrib.auth.models import Permission


class AuthenticationTests(APITestCase):
    # TODO 1: Testear login fallido, agregar GRUPO!
    def setUp(self):
        '''
            Creo el usuario, le doy permisos de creacion de usuarios
            Lo logeo creando el Token 
        '''
        self.client = APIClient()
        self.group = Group.objects.create(name="Docente")
        self.group.save()
        self.group.permissions.add(Permission.objects.get(name="Can add user"))
        self.user = User.objects.create_user(
            'juan@juan.com', password='juan123', groups=self.group)
        self.token = Token.objects.create(user=self.user)

    def test_login(self):
        user = {
            'username': 'juan@juan.com',
            'password': 'juan123'
        }
        response = self.client.post('/api/users/login/', data=user)
        self.assertEqual(self.token.key, response.data['token'])

    def test_register_while_logged_in_and_valid_data(self):
        new_user = {
            'email': "pedro@pedro.com",
            'password': "pedrito123",
            'password2': "pedrito123",
            "groups": self.group.id
        }
        response = self.client.post(
            '/api/users/register/',
            data=new_user, format='json',
            HTTP_AUTHORIZATION="Token "+self.token.key)
        self.assertEqual(response.status_code, 201)

    def test_register_while_logged_in_and_non_matching_passwords(self):
        new_user = {
            'email': "pedro@pedro.com",
            'password': "pedrito123",
            'password2': "a",
            "groups": self.group.id
        }
        response = self.client.post(
            '/api/users/register/',
            data=new_user, format='json',
            HTTP_AUTHORIZATION="Token "+self.token.key)
        self.assertEqual(response.status_code, 400)

    def test_logout_successful(self):
        response = self.client.get(
            '/api/users/logout/', HTTP_AUTHORIZATION="Token " + self.token.key)

        self.assertEqual(response.status_code, 200)

    def test_logout_unauthorized(self):
        response = self.client.get(
            '/api/users/logout/', HTTP_AUTHORIZATION="not_a_token")
        self.assertEqual(response.status_code, 401)


class PermissionsTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.group_docente = Group.objects.create(name="Docente")
        self.group_docente.save()
        self.group_docente.permissions.add(
            Permission.objects.get(name="Can add user"))
        self.group_otro = Group.objects.create(name="Otro")

    def test_forbidden_action(self):
        user = User.objects.create_user(
            'juan@juan.com', password='juan123', groups=self.group_otro)
        token = Token.objects.create(user=user)
        new_user = {
            'email': "pedro@pedro.com",
            'password': "pedrito123",
            'password2': "pedrito123",
            "groups": self.group_docente.id
        }
        response = self.client.post(
            '/api/users/register/',
            data=new_user, format='json',
            HTTP_AUTHORIZATION="Token " + token.key)
        self.assertEqual(response.status_code, 403)

    def test_permitted_action(self):
        user = User.objects.create_user(
            'juan@juan.com', password='juan123', groups=self.group_docente)
        token = Token.objects.create(user=user)
        new_user = {
            'email': "pedro@pedro.com",
            'password': "pedrito123",
            'password2': "pedrito123",
            "groups": self.group_docente.id
        }
        response = self.client.post(
            '/api/users/register/',
            data=new_user, format='json',
            HTTP_AUTHORIZATION="Token " + token.key)
        self.assertEqual(response.status_code, 201)
