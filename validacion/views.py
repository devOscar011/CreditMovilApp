from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import Persona, Solicitud, Amortizacion
from .permissions import IsAdminGroup
from django.shortcuts import render
from rest_framework import viewsets

from .permissions import GroupPermission
from .models import (
    Persona, Solicitud, Laboral, Domicilio, Conyuge,
    GastosMensuales, ReferenciaPersonal, User, Amortizacion
)

from .serializers import (
    PersonaDetalleCompletoSerializer, PersonaSerializer, RegisterSerializer, SolicitudSerializer,
    LaboralSerializer, DomicilioSerializer, ConyugeSerializer, GastosMensualesSerializer,
    ReferenciaPersonalSerializer, UserSerializer, AmortizacionSerializer
)

from rest_framework_simplejwt.tokens import RefreshToken


# -----------------------------------------------------
#                  AUTH / USERS
# -----------------------------------------------------

class LogoutView(APIView):
    permission_classes = [IsAuthenticated, GroupPermission]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout exitoso"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    #permission_classes = [IsAuthenticated, GroupPermission]
    permission_classes = [IsAuthenticated, IsAdminGroup]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = RefreshToken.for_user(user)
            data = {
                "user": UserSerializer(user).data,
                "refresh": str(token),
                "access": str(token.access_token),
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------
#                PERSONA DETALLE COMPLETO
# -----------------------------------------------------

class PersonaDetalleCompletoView(APIView):
    permission_classes = [IsAuthenticated, GroupPermission]

    def get(self, request, persona_id):
        try:
            persona = Persona.objects.get(id=persona_id)
        except Persona.DoesNotExist:
            return Response({'detail': 'Persona no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PersonaDetalleCompletoSerializer(persona)
        return Response(serializer.data)


# -----------------------------------------------------
#              TABLA AMORTIZACIÓN
# -----------------------------------------------------

class TablaAmortizacionCalculada(APIView):
    permission_classes = [IsAuthenticated, GroupPermission]

    def get(self, request, persona_id):
        try:
            persona = Persona.objects.get(pk=persona_id)
        except Persona.DoesNotExist:
            return Response({"detail": "Persona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        solicitud = Solicitud.objects.filter(IdPersona=persona).first()
        if not solicitud:
            return Response({"detail": "No se encontró solicitud"}, status=status.HTTP_404_NOT_FOUND)

        P = float(solicitud.MontoSolicitado)
        n = solicitud.PlazoFinanciero
        tasa_anual = float(solicitud.TasaInteresAnual)
        r = tasa_anual / 100 / 12

        cuota = (P * (r * (1 + r)**n) / ((1 + r)**n - 1)) if r > 0 else P / n
        cuota = round(cuota, 2)

        tabla = []
        saldo = P

        for mes in range(1, n + 1):
            interes = round(saldo * r, 2)
            capital = round(cuota - interes, 2)
            saldo = round(saldo - capital, 2)
            tabla.append({
                "Mes": mes,
                "Cuota": cuota,
                "Capital": capital,
                "Interes": interes,
                "CapitalVivo": max(saldo, 0),
            })

        return Response({
            "Persona": f"{persona.Nombres} {persona.Apellidos}",
            "MontoSolicitado": P,
            "PlazoMeses": n,
            "TasaAnual": tasa_anual,
            "TablaAmortizacion": tabla,
        })


# -----------------------------------------------------
#                    CRUD VIEWSETS
# -----------------------------------------------------

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminGroup]


class PersonaViewSet(viewsets.ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer
    permission_classes = [IsAuthenticated, GroupPermission]


class SolicitudViewSet(viewsets.ModelViewSet):
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer
    permission_classes = [IsAuthenticated, GroupPermission]


class LaboralViewSet(viewsets.ModelViewSet):
    queryset = Laboral.objects.all()
    serializer_class = LaboralSerializer
    permission_classes = [IsAuthenticated, GroupPermission]


class DomicilioViewSet(viewsets.ModelViewSet):
    queryset = Domicilio.objects.all()
    serializer_class = DomicilioSerializer
    permission_classes = [IsAuthenticated, GroupPermission]


class ConyugeViewSet(viewsets.ModelViewSet):
    queryset = Conyuge.objects.all()
    serializer_class = ConyugeSerializer
    permission_classes = [IsAuthenticated, GroupPermission]


class GastosMensualesViewSet(viewsets.ModelViewSet):
    queryset = GastosMensuales.objects.all()
    serializer_class = GastosMensualesSerializer
    permission_classes = [IsAuthenticated, GroupPermission]


class ReferenciaPersonalViewSet(viewsets.ModelViewSet):
    queryset = ReferenciaPersonal.objects.all()
    serializer_class = ReferenciaPersonalSerializer
    permission_classes = [IsAuthenticated, GroupPermission]


# -----------------------------------------------------
#        FUNCIONES FINANCIERAS (Views protegidas)
# -----------------------------------------------------

class EvaluarCapacidadPagoAPIView(APIView):
    permission_classes = [IsAuthenticated, GroupPermission]

    def get(self, request, persona_id):
        query = "SELECT * FROM EvaluarCapacidadPagoReal(%s);"
        with connection.cursor() as cursor:
            cursor.execute(query, [persona_id])
            row = cursor.fetchone()

        if not row:
            return Response({"detail": "No se encontraron datos"}, status=status.HTTP_404_NOT_FOUND)

        (
            persona_id,
            ingreso_total,
            gastos_totales,
            flujo_caja_libre,
            cuota_mensual,
            dscr,
            estado_credito
        ) = row

        return Response({
            "PersonaId": persona_id,
            "IngresosMensualesTotales": float(ingreso_total),
            "GastosMensualesTotales": float(gastos_totales),
            "FlujoCajaLibre": float(flujo_caja_libre),
            "CuotaMensual": float(cuota_mensual),
            "DSCR": float(dscr) if dscr is not None else None,
            "EstadoCredito": estado_credito
        })


class AnalizarFlujoDeCajaAPIView(APIView):
    permission_classes = [IsAuthenticated, GroupPermission]

    def get(self, request, persona_id):
        query = "SELECT * FROM AnalizarFlujoDeCaja(%s);"
        with connection.cursor() as cursor:
            cursor.execute(query, [persona_id])
            row = cursor.fetchone()

        if not row:
            return Response({"detail": "No se encontraron datos"}, status=status.HTTP_404_NOT_FOUND)

        persona_id, ingreso, gastos, flujo = row

        return Response({
            "PersonaId": persona_id,
            "IngresoMensual": float(ingreso),
            "GastosMensuales": float(gastos),
            "FlujoCajaLibre": float(flujo)
        })


class CalcularIndiceEndeudamiento(APIView):
    permission_classes = [IsAuthenticated, GroupPermission]

    def get(self, request, persona_id):
        query = "SELECT * FROM CalcularIndiceEndeudamiento(%s);"
        with connection.cursor() as cursor:
            cursor.execute(query, [persona_id])
            row = cursor.fetchone()

        if not row:
            return Response({"detail": "No se encontraron datos"}, status=status.HTTP_404_NOT_FOUND)

        persona_id, ingresos, gastos, indice, evaluacion_bd = row

        if indice is not None:
            if indice <= 0.20:
                evaluacion = "Muy bajo: Buena salud financiera"
            elif indice <= 0.35:
                evaluacion = "Aceptable: Manejo prudente de la deuda"
            elif indice <= 0.50:
                evaluacion = "Alto: Riesgo potencial de sobreendeudamiento"
            else:
                evaluacion = "Muy alto: Riesgo significativo de insolvencia"
        else:
            evaluacion = "Datos insuficientes"

        return Response({
            "PersonaId": persona_id,
            "IngresoMensual": float(ingresos),
            "GastosMensuales": float(gastos),
            "IndiceEndeudamiento": float(indice) if indice is not None else None,
            "EvaluacionEndeudamiento": evaluacion
        })


class CalcularLTVAPIView(APIView):
    permission_classes = [IsAuthenticated, GroupPermission]

    def get(self, request, id_persona):
        query = """SELECT MontoPrestamo, MontoGarantia, LTV, Interpretacion 
                   FROM CalcularLTV(%s);"""
        with connection.cursor() as cursor:
            cursor.execute(query, [id_persona])
            row = cursor.fetchone()

        if not row:
            return Response({"error": "No se encontraron datos"}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "MontoPrestamo": float(row[0]) if row[0] else None,
            "MontoGarantia": float(row[1]) if row[1] else None,
            "LTV": float(row[2]) if row[2] else None,
            "Interpretacion": row[3],
        })


class AnalizarSensibilidadAPIView(APIView):
    permission_classes = [IsAuthenticated, GroupPermission]

    def post(self, request):
        id_persona = request.data.get('id_persona')
        variacion = request.data.get('variacion_escenario')

        if id_persona is None or variacion is None:
            return Response({"error": "Datos faltantes"}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM AnalizarSensibilidad(%s, %s)", [id_persona, variacion])
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        if not row:
            return Response({"error": "Sin datos"}, status=status.HTTP_404_NOT_FOUND)

        return Response(dict(zip(columns, row)))


class PruebasDeEstresAPIView(APIView):
    permission_classes = [IsAuthenticated, GroupPermission]

    def post(self, request):
        id_persona = request.data.get('id_persona')
        r_ingresos = request.data.get('reduccion_ingresos')
        i_gastos = request.data.get('incremento_gastos')
        i_tasa = request.data.get('incremento_tasa_interes')

        if None in (id_persona, r_ingresos, i_gastos, i_tasa):
            return Response({"error": "Datos incompletos"}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM PruebasDeEstres(%s, %s, %s, %s)
            """, [id_persona, r_ingresos, i_gastos, i_tasa])
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        if not row:
            return Response({"error": "No se encontraron resultados"}, status=status.HTTP_404_NOT_FOUND)

        return Response(dict(zip(columns, row)))
    ##Edpoint para reporte de tabla de amortizacion
class ReporteCreditoPDF(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, persona_id):
        # Obtener los datos personales
        try:
            persona = Persona.objects.get(pk=persona_id)
        except Persona.DoesNotExist:
            return Response({"detail": "Persona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        # Obtener la solicitud asociada a la persona
        solicitud = Solicitud.objects.filter(IdPersona=persona).first()
        if not solicitud:
            return Response({"detail": "No se encontró solicitud"}, status=status.HTTP_404_NOT_FOUND)

        # Obtener la tabla de amortización
        amortizaciones = Amortizacion.objects.filter(IdPersona=persona).order_by('Mes')

        # Crear el PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Usar una fuente estándar para evitar problemas con la codificación
        p.setFont("Helvetica", 10)

        # Datos del crédito y persona
        p.drawString(100, 750, f"Nombre: {persona.Nombres} {persona.Apellidos}")
        p.drawString(100, 730, f"Tipo de Identificación: {persona.TipoIdentificacion}")
        p.drawString(100, 710, f"Numero de Identificación: {persona.NumeroIdentificacion}")
        p.drawString(100, 690, f"Estado Civil: {persona.EstadoCivil}")
        p.drawString(100, 670, f"Sexo: {persona.Sexo}")
        p.drawString(100, 650, f"Nacionalidad: {persona.Nacionalidad}")
        p.drawString(100, 630, f"Fecha de Nacimiento: {persona.FechaNacimiento}")

        p.drawString(100, 610, f"Solicitud No: {solicitud.NumeroSolicitud}")
        p.drawString(100, 590, f"Monto Solicitado: ${solicitud.MontoSolicitado}")
        p.drawString(100, 570, f"Plazo: {solicitud.PlazoFinanciero} meses")
        p.drawString(100, 550, f"Tasa de Interés Anual: {solicitud.TasaInteresAnual}%")
        p.drawString(100, 530, f"Propósito del Préstamo: {solicitud.PropositoPrestamo}")

        # Tabla de Amortización
        p.drawString(100, 510, "Tabla de Amortización:")
        y_position = 490
        p.drawString(100, y_position, "Mes   Cuota   Capital   Interes   Capital Vivo")
        y_position -= 20

        # Imprimir la tabla de amortización
        for amort in amortizaciones:
            y_position -= 20
            p.drawString(100, y_position, f"{amort.Mes}   {amort.Cuota}   {amort.Capital}   {amort.Interes}   {amort.CapitalVivo}")

        # Guardar el PDF
        p.showPage()
        p.save()

        # Volver al inicio del buffer para leerlo
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()

        # Devolver el PDF como respuesta
        response = Response(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_credito.pdf"'
        return response