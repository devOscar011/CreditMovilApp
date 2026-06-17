from datetime import datetime
from email.headerregistry import Group
from io import BytesIO
import base64

from django.db import connection
from django.http import HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.db import connection
from django.contrib.auth.models import User, Group 

from .models import (
    Persona, Solicitud, Amortizacion, Laboral, Domicilio, Conyuge,
    GastosMensuales, ReferenciaPersonal, User
)
from .permissions import IsAdminGroup, GroupPermission

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

class GroupListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminGroup]
    
    def get(self, request):
        try:
            # Usar Group de django.contrib.auth.models
            groups = Group.objects.all().values('id', 'name')
            return Response(list(groups))
        except Exception as e:
            print(f"Error obteniendo grupos: {e}")
            # Si no funciona, devolver grupos por defecto
            default_groups = [
                {"id": 1, "name": "Administrador"},
                {"id": 2, "name": "Analista"},
                {"id": 3, "name": "Consultor"},
            ]
            return Response(default_groups)


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

class TestAmortizacion(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, persona_id):
        # Verificar datos en tabla Amortizacion
        amortizaciones = Amortizacion.objects.filter(IdPersona_id=persona_id).order_by('Mes')
        print(f"Total amortizaciones en BD: {amortizaciones.count()}")
        
        # Verificar si hay una solicitud
        solicitud = Solicitud.objects.filter(IdPersona_id=persona_id).first()
        print(f"Solicitud encontrada: {solicitud}")
        
        return Response({
            "amortizaciones_en_bd": amortizaciones.count(),
            "solicitud": solicitud.NumeroSolicitud if solicitud else None
        })
    
class ReporteCreditoPDFProfesional(APIView):
    """
    Endpoint único que funciona para Web y Móvil (Expo).
    Detecta automáticamente el tipo de cliente y devuelve la respuesta adecuada.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, persona_id):
        try:
            # Obtener datos de la persona
            try:
                persona = Persona.objects.get(pk=persona_id)
            except Persona.DoesNotExist:
                return self._respond_error("Persona no encontrada", status.HTTP_404_NOT_FOUND, request)

            # Obtener solicitud
            solicitud = Solicitud.objects.filter(IdPersona=persona).first()
            if not solicitud:
                return self._respond_error("No se encontró solicitud", status.HTTP_404_NOT_FOUND, request)

            # Obtener o calcular amortizaciones
            amortizaciones_db = Amortizacion.objects.filter(IdPersona=persona).order_by('Mes')
            
            if not amortizaciones_db.exists():
                amortizaciones = self._calcular_amortizacion(solicitud)
            else:
                amortizaciones = list(amortizaciones_db)

            # Generar PDF
            pdf_bytes = self._generar_pdf(persona, solicitud, amortizaciones)
            
            # Determinar tipo de cliente (web o móvil)
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
            is_mobile_app = 'expo' in user_agent or 'reactnative' in user_agent
            is_mobile_request = request.query_params.get('mobile', 'false').lower() == 'true'
            
            # También verificar por header personalizado
            is_expo_request = request.META.get('HTTP_X_REQUESTED_WITH') == 'Expo'
            
            # Si es solicitud móvil o Expo
            if is_mobile_app or is_mobile_request or is_expo_request:
                return self._respond_for_mobile(pdf_bytes, persona, solicitud)
            else:
                return self._respond_for_web(pdf_bytes, persona)

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error generando PDF: {error_details}")
            
            return self._respond_error(
                f"Error interno: {str(e)}", 
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                request
            )

    def _respond_for_web(self, pdf_bytes, persona):
        """Respuesta para navegadores web - descarga directa"""
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        filename = f"Informe_Credito_{persona.NumeroIdentificacion[:10]}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf_bytes)
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response

    def _respond_for_mobile(self, pdf_bytes, persona, solicitud):
        """Respuesta para móvil/Expo - JSON con base64"""
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # También opcionalmente guardar el archivo temporalmente para descarga directa
        import tempfile
        import os
        from django.conf import settings
        
        # Crear archivo temporal para descarga opcional
        temp_filename = None
        if hasattr(settings, 'MEDIA_ROOT'):
            import uuid
            temp_filename = f"temp_pdf_{uuid.uuid4().hex[:8]}.pdf"
            temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_pdfs', temp_filename)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            with open(temp_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return Response({
            "success": True,
            "pdf_base64": pdf_base64,
            "filename": f"Informe_Credito_{persona.NumeroIdentificacion[:10]}.pdf",
            "file_size": len(pdf_bytes),
            "file_size_mb": f"{(len(pdf_bytes) / 1024 / 1024):.2f}",
            "temp_url": f"/media/temp_pdfs/{temp_filename}" if temp_filename else None,
            "persona": {
                "id": persona.IdPersona,
                "nombre": f"{persona.Nombres} {persona.Apellidos}",
                "identificacion": persona.NumeroIdentificacion
            },
            "solicitud": {
                "numero": getattr(solicitud, 'NumeroSolicitud', 'N/A'),
                "monto": float(getattr(solicitud, 'MontoSolicitado', 0)) if getattr(solicitud, 'MontoSolicitado', 0) else 0
            },
            "timestamp": datetime.now().isoformat(),
            "format": "base64",
            "instructions": {
                "expo": "Usa expo-file-system para guardar el base64",
                "web": "Usa atob() para decodificar el base64"
            }
        })

    def _respond_error(self, message, status_code, request=None):
        """Manejo de errores unificado"""
        if request and self._is_mobile_request(request):
            return Response({
                "success": False,
                "error": message,
                "timestamp": datetime.now().isoformat()
            }, status=status_code)
        else:
            return Response({
                "error": message
            }, status=status_code)

    def _is_mobile_request(self, request):
        """Determina si es una solicitud móvil"""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        is_mobile_app = 'expo' in user_agent or 'reactnative' in user_agent
        is_mobile_param = request.query_params.get('mobile', 'false').lower() == 'true'
        is_expo_header = request.META.get('HTTP_X_REQUESTED_WITH') == 'Expo'
        
        return is_mobile_app or is_mobile_param or is_expo_header

    def _generar_pdf(self, persona, solicitud, amortizaciones):
        """Genera el PDF y retorna los bytes"""
        buffer = BytesIO()
        
        # Configurar página A4
        width, height = A4
        
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # ====================
        # PORTADA
        # ====================
        p.setFont("Helvetica-Bold", 24)
        p.setFillColor(colors.HexColor('#1a365d'))
        p.drawCentredString(width/2, height - 80, "INFORMACIÓN SOBRE SU CRÉDITO")
        
        # Fecha y ciudad
        p.setFont("Helvetica", 10)
        p.setFillColor(colors.black)
        p.drawString(100, height - 110, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        p.drawString(width - 200, height - 110, f"Ciudad: Managua")
        
        # Línea decorativa
        p.setStrokeColor(colors.HexColor('#1a365d'))
        p.setLineWidth(2)
        p.line(50, height - 130, width - 50, height - 130)
        
        # ====================
        # INFORMACIÓN DEL BANCO
        # ====================
        y = height - 160
        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(colors.HexColor('#1a365d'))
        p.drawCentredString(width/2, y, "BANCO Anomimo S.A.")
        y -= 25
        
        p.setFont("Helvetica-Oblique", 12)
        p.setFillColor(colors.HexColor('#4a5568'))
        p.drawCentredString(width/2, y, "Más banco. Más amigo.")
        
        # ====================
        # DATOS GENERALES DEL CRÉDITO
        # ====================
        y -= 50
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(colors.HexColor('#1a365d'))
        p.drawString(50, y, "DATOS GENERALES DEL CRÉDITO")
        y -= 30
        
        # Datos generales
        numero_solicitud = getattr(solicitud, 'NumeroSolicitud', 'N/A')
        
        # Fecha
        fecha_desembolso = self._obtener_fecha_solicitud(solicitud)
        
        datos_generales = [
            ("Crédito Nº", numero_solicitud),
            ("Nombre del cliente", f"{persona.Nombres} {persona.Apellidos}"),
            ("Número de identificación", f"{getattr(persona, 'TipoIdentificacion', 'ID')}: {persona.NumeroIdentificacion}"),
            ("Fecha del desembolso", fecha_desembolso),
            ("Oficina", "SEDE PRINCIPAL"),
            ("Usuario", f"{persona.NumeroIdentificacion[:8]} {persona.Nombres[:10]}")
        ]
        
        for label, value in datos_generales:
            p.setFont("Helvetica-Bold", 10)
            p.setFillColor(colors.HexColor('#2d3748'))
            p.drawString(70, y, f"{label}:")
            p.setFont("Helvetica", 10)
            p.setFillColor(colors.black)
            p.drawString(200, y, str(value)[:40])
            y -= 20
        
        # ====================
        # CONDICIONES FINANCIERAS
        # ====================
        y -= 30
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(colors.HexColor('#1a365d'))
        p.drawString(50, y, "CONDICIONES FINANCIERAS")
        y -= 30
        
        # Calcular valores financieros
        monto = float(getattr(solicitud, 'MontoSolicitado', 0)) if getattr(solicitud, 'MontoSolicitado', 0) else 0
        plazo = getattr(solicitud, 'PlazoFinanciero', 0) if getattr(solicitud, 'PlazoFinanciero', 0) else 0
        tasa_anual = float(getattr(solicitud, 'TasaInteresAnual', 0)) if getattr(solicitud, 'TasaInteresAnual', 0) else 0
        
        # Calcular cuota
        cuota_mensual, total_intereses, costo_total = self._calcular_cuota(monto, plazo, tasa_anual)
        
        # Tabla de condiciones
        condiciones = [
            ("Importe del préstamo", f"${monto:,.0f}" if monto > 0 else "$0"),
            ("Tasa de interés anual", f"{tasa_anual:.2f}%" if tasa_anual > 0 else "0.00%"),
            ("INTERÉS NOMINAL MENSUAL", f"{tasa_anual/12:.2f}%" if tasa_anual > 0 else "0.00%"),
            ("Plazo en años", f"{plazo/12:.1f}" if plazo > 0 else "0"),
            ("Fecha de inicio", fecha_desembolso),
            ("Pago mensual", f"${cuota_mensual:,.0f}" if cuota_mensual > 0 else "$0"),
            ("Plazo en meses", f"{plazo}" if plazo > 0 else "0"),
            ("Total intereses", f"${total_intereses:,.0f}" if total_intereses > 0 else "$0"),
            ("Coste total", f"${costo_total:,.0f}" if costo_total > 0 else "$0"),
            ("Seguro del crédito", "0,009")
        ]
        
        for i, (label, value) in enumerate(condiciones):
            col_x = 70 if i % 2 == 0 else 300
            row_y = y - ((i // 2) * 20)
            
            p.setFont("Helvetica-Bold", 9)
            p.setFillColor(colors.HexColor('#4a5568'))
            p.drawString(col_x, row_y, label)
            p.setFont("Helvetica", 9)
            p.setFillColor(colors.black)
            p.drawString(col_x + 130, row_y, str(value))
        
        # ====================
        # TABLA DE AMORTIZACIÓN
        # ====================
        if amortizaciones:
            p.showPage()
            
            p.setFont("Helvetica-Bold", 16)
            p.setFillColor(colors.HexColor('#1a365d'))
            p.drawCentredString(width/2, height - 50, "TABLA DE AMORTIZACIÓN")
            
            y = height - 80
            
            # Encabezados
            headers = ["MES", "FECHA", "CUOTA", "INTERÉS", "CAPITAL", "SALDO"]
            col_widths = [50, 90, 80, 80, 100, 100]
            col_positions = [50]
            
            for i in range(1, len(col_widths)):
                col_positions.append(col_positions[i-1] + col_widths[i-1])
            
            # Encabezados
            p.setFillColor(colors.HexColor('#2d3748'))
            p.rect(50, y - 20, width - 100, 25, fill=1, stroke=0)
            
            p.setFont("Helvetica-Bold", 8)
            p.setFillColor(colors.white)
            for i, header in enumerate(headers):
                p.drawString(col_positions[i] + 5, y - 15, header)
            
            y -= 35
            
            # Datos
            p.setFont("Helvetica", 8)
            
            for i, amort in enumerate(amortizaciones[:30]):
                if y < 50:
                    p.showPage()
                    y = height - 50
                    
                    # Redibujar encabezados
                    p.setFillColor(colors.HexColor('#2d3748'))
                    p.rect(50, y - 20, width - 100, 25, fill=1, stroke=0)
                    p.setFont("Helvetica-Bold", 8)
                    p.setFillColor(colors.white)
                    for j, header in enumerate(headers):
                        p.drawString(col_positions[j] + 5, y - 15, header)
                    y -= 35
                    p.setFont("Helvetica", 8)
                
                # Color de fondo alternado
                if i % 2 == 0:
                    p.setFillColor(colors.HexColor('#f8fafc'))
                else:
                    p.setFillColor(colors.white)
                
                p.rect(50, y - 15, width - 100, 20, fill=1, stroke=0)
                
                # Extraer valores
                mes, cuota_val, interes_val, capital_val, saldo_val = self._extraer_valores_amortizacion(amort, i)
                
                # Fecha aproximada
                fecha_cuota = datetime.now().replace(day=3)
                
                # Texto
                p.setFillColor(colors.black)
                p.drawString(col_positions[0] + 5, y - 10, str(mes))
                p.drawString(col_positions[1] + 5, y - 10, fecha_cuota.strftime('%d/%m/%Y'))
                p.drawString(col_positions[2] + 5, y - 10, f"${cuota_val:,.0f}")
                p.drawString(col_positions[3] + 5, y - 10, f"${interes_val:,.0f}")
                p.drawString(col_positions[4] + 5, y - 10, f"${capital_val:,.0f}")
                p.drawString(col_positions[5] + 5, y - 10, f"${saldo_val:,.0f}")
                
                y -= 25
        else:
            # Sin amortizaciones
            p.showPage()
            p.setFont("Helvetica-Bold", 14)
            p.setFillColor(colors.red)
            p.drawCentredString(width/2, height/2, "NO HAY DATOS DE AMORTIZACIÓN DISPONIBLES")
        
        # Pie de página final
        p.showPage()
        p.setFont("Helvetica", 10)
        p.setFillColor(colors.HexColor('#6b7280'))
        p.drawCentredString(width/2, 50, f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        p.drawCentredString(width/2, 35, "Banco Financiero S.A. - Más banco. Más amigo.")
        
        # Guardar PDF
        p.save()
        
        # Obtener bytes
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes

    # ========== MÉTODOS AUXILIARES ==========
    
    def _obtener_fecha_solicitud(self, solicitud):
        """Obtiene la fecha de la solicitud de diferentes campos posibles"""
        for attr in ['FechaSolicitud', 'fecha_solicitud', 'fecha', 'created_at', 'FechaCreacion']:
            if hasattr(solicitud, attr):
                value = getattr(solicitud, attr)
                if value:
                    return value.strftime('%d/%m/%Y')
        return "N/A"

    def _calcular_cuota(self, monto, plazo, tasa_anual):
        """Calcula la cuota mensual"""
        if monto > 0 and plazo > 0 and tasa_anual > 0:
            tasa_mensual = tasa_anual / 12 / 100
            try:
                cuota = (monto * (tasa_mensual * (1 + tasa_mensual)**plazo)) / (((1 + tasa_mensual)**plazo) - 1)
                cuota_mensual = round(cuota, 2)
                total_intereses = (cuota_mensual * plazo) - monto
                costo_total = cuota_mensual * plazo
                return cuota_mensual, total_intereses, costo_total
            except:
                cuota_mensual = monto / plazo if plazo > 0 else 0
                return cuota_mensual, 0, monto
        else:
            cuota_mensual = monto / plazo if plazo > 0 else 0
            return cuota_mensual, 0, monto

    def _extraer_valores_amortizacion(self, amort, index):
        """Extrae valores de la amortización de forma segura"""
        try:
            if isinstance(amort, dict):
                mes = amort.get('Mes', index + 1)
                cuota = amort.get('Cuota', 0)
                capital = amort.get('Capital', 0)
                interes = amort.get('Interes', 0)
                saldo = amort.get('CapitalVivo', 0) or amort.get('Saldo', 0)
            else:
                mes = amort.Mes if hasattr(amort, 'Mes') and amort.Mes else index + 1
                cuota = amort.Cuota if hasattr(amort, 'Cuota') else 0
                capital = amort.Capital if hasattr(amort, 'Capital') else 0
                interes = amort.Interes if hasattr(amort, 'Interes') else 0
                saldo = amort.CapitalVivo if hasattr(amort, 'CapitalVivo') else (
                    amort.Saldo if hasattr(amort, 'Saldo') else 0
                )
        except:
            mes = index + 1
            cuota = capital = interes = saldo = 0
        
        cuota_val = float(cuota) if cuota else 0
        interes_val = float(interes) if interes else 0
        capital_val = float(capital) if capital else 0
        saldo_val = float(saldo) if saldo else 0
        
        return mes, cuota_val, interes_val, capital_val, saldo_val

    def _calcular_amortizacion(self, solicitud):
        """Calcular tabla de amortización si no existe en BD"""
        try:
            P = float(getattr(solicitud, 'MontoSolicitado', 0)) if getattr(solicitud, 'MontoSolicitado', 0) else 0
            n = getattr(solicitud, 'PlazoFinanciero', 0) if getattr(solicitud, 'PlazoFinanciero', 0) else 0
            tasa_anual = float(getattr(solicitud, 'TasaInteresAnual', 0)) if getattr(solicitud, 'TasaInteresAnual', 0) else 0
            
            if P <= 0 or n <= 0:
                return []
            
            r = tasa_anual / 100 / 12 if tasa_anual > 0 else 0.01 / 12
            
            # Calcular cuota
            if r > 0:
                cuota = (P * (r * (1 + r)**n)) / (((1 + r)**n) - 1)
            else:
                cuota = P / n if n > 0 else 0
            
            cuota = round(cuota, 2)
            saldo = P
            tabla = []
            
            for mes in range(1, min(n, 360) + 1):
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
            
            return tabla
        except Exception as e:
            print(f"Error calculando amortización: {e}")
            return []