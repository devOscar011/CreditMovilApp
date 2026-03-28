from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from validacion.models import (Conyuge, Domicilio, GastosMensuales, Laboral,
                               Persona, ReferenciaPersonal, Solicitud)


class BaseAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

class PersonaTests(BaseAPITest):
    def test_create_persona(self):
        data = {
            "Nombres": "Juan",
            "Apellidos": "Pérez",
            "TipoIdentificacion": "DNI",
            "NumeroIdentificacion": "12345678",
            "Nacionalidad": "Argentina",
            "FechaNacimiento": "1990-01-01",
            "EstadoCivil": "Soltero",
            "Sexo": "M",
        }
        response = self.client.post("/api/personas/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_personas(self):
        response = self.client.get("/api/personas/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class SolicitudTests(BaseAPITest):
    def test_create_solicitud(self):
        persona = Persona.objects.create(
            Nombres="Ana", Apellidos="Gómez",
            TipoIdentificacion="DNI", NumeroIdentificacion="87654321",
            Nacionalidad="Argentina", FechaNacimiento="1992-05-10",
            EstadoCivil="Casado", Sexo="F"
        )
        data = {
            "NumeroSolicitud": "SOL-001",
            "TipoMoneda": "ARS",
            "MontoSolicitado": 100000,
            "PlazoFinanciero": 12,
            "PropositoPrestamo": "Compra de vehículo",
            "TasaInteresAnual": 10.5,
            "Estado": "Pendiente",
            "IdPersona": persona.id,
        }
        response = self.client.post("/api/solicitudes/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class LaboralTests(BaseAPITest):
    def test_list_laboral(self):
        response = self.client.get("/api/laborales/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class DomicilioTests(BaseAPITest):
    def test_list_domicilios(self):
        response = self.client.get("/api/domicilios/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ConyugeTests(BaseAPITest):
    def test_list_conyuges(self):
        response = self.client.get("/api/conyuges/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GastosMensualesTests(BaseAPITest):
    def test_list_gastos(self):
        response = self.client.get("/api/gastos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ReferenciaPersonalTests(BaseAPITest):
    def test_list_referencias(self):
        response = self.client.get("/api/referencias/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RegistroUsuarioTests(APITestCase):
    def setUp(self):
        self.admin_group, _ = Group.objects.get_or_create(name="Admin")
        self.admin_user = User.objects.create_user(
            username="adminuser",
            password="adminpass123",
            email="admin@example.com",
        )
        self.admin_user.groups.add(self.admin_group)
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

    def test_no_permite_email_duplicado(self):
        User.objects.create_user(
            username="user1",
            password="testpass123",
            email="dup@example.com",
        )

        data = {
            "username": "user2",
            "email": "dup@example.com",
            "password": "testpass123",
            "password2": "testpass123",
        }
        response = self.client.post("/api/registro/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
