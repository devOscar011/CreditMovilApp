from datetime import datetime
from email.headerregistry import Group
from io import BytesIO

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
    permission_classes = [IsAuthenticated]

    def get(self, request, persona_id):
        try:
            persona = Persona.objects.get(pk=persona_id)
        except Persona.DoesNotExist:
            return Response({"detail": "Persona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        solicitud = Solicitud.objects.filter(IdPersona=persona).first()
        if not solicitud:
            return Response({"detail": "No se encontró solicitud"}, status=status.HTTP_404_NOT_FOUND)

        # Obtener amortizaciones de la base de datos
        amortizaciones_db = Amortizacion.objects.filter(IdPersona=persona).order_by('Mes')
        
        # Si no hay amortizaciones en la BD, calcularlas
        if not amortizaciones_db.exists():
            amortizaciones = self.calcular_amortizacion(solicitud)
        else:
            amortizaciones = list(amortizaciones_db)

        # Crear buffer para el PDF
        buffer = BytesIO()
        
        # Configurar página A4
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        width, height = A4
        
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # ====================
        # PORTADA - Formato profesional
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
        
        # Usar solo campos que existen en el modelo Solicitud
        # Verificar qué campos tiene realmente el modelo
        numero_solicitud = getattr(solicitud, 'NumeroSolicitud', 'N/A')
        
        # Intentar obtener fecha de diferentes campos posibles
        fecha_desembolso = "N/A"
        if hasattr(solicitud, 'FechaSolicitud'):
            fecha_desembolso = solicitud.FechaSolicitud.strftime('%d/%m/%Y') if solicitud.FechaSolicitud else "N/A"
        elif hasattr(solicitud, 'fecha_solicitud'):
            fecha_desembolso = solicitud.fecha_solicitud.strftime('%d/%m/%Y') if solicitud.fecha_solicitud else "N/A"
        elif hasattr(solicitud, 'fecha'):
            fecha_desembolso = solicitud.fecha.strftime('%d/%m/%Y') if solicitud.fecha else "N/A"
        elif hasattr(solicitud, 'created_at'):
            fecha_desembolso = solicitud.created_at.strftime('%d/%m/%Y') if solicitud.created_at else "N/A"
        
        # Cuadro de datos generales - Solo campos que existen
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
            p.drawString(200, y, str(value)[:40])  # Limitar longitud
            y -= 20
        
        # ====================
        # CONDICIONES FINANCIERAS
        # ====================
        y -= 30
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(colors.HexColor('#1a365d'))
        p.drawString(50, y, "CONDICIONES FINANCIERAS")
        y -= 30
        
        # Calcular valores financieros usando solo campos existentes
        monto = float(getattr(solicitud, 'MontoSolicitado', 0)) if getattr(solicitud, 'MontoSolicitado', 0) else 0
        plazo = getattr(solicitud, 'PlazoFinanciero', 0) if getattr(solicitud, 'PlazoFinanciero', 0) else 0
        tasa_anual = float(getattr(solicitud, 'TasaInteresAnual', 0)) if getattr(solicitud, 'TasaInteresAnual', 0) else 0
        
        # Evitar división por cero
        tasa_mensual = tasa_anual / 12 / 100 if tasa_anual > 0 else 0.01 / 12
        
        # Calcular pago mensual aproximado
        if tasa_mensual > 0 and plazo > 0 and monto > 0:
            try:
                cuota = (monto * (tasa_mensual * (1 + tasa_mensual)**plazo)) / (((1 + tasa_mensual)**plazo) - 1)
                cuota_mensual = round(cuota, 2)
                total_intereses = (cuota_mensual * plazo) - monto
                costo_total = cuota_mensual * plazo
            except:
                cuota_mensual = monto / plazo if plazo > 0 else 0
                total_intereses = 0
                costo_total = monto
        else:
            cuota_mensual = monto / plazo if plazo > 0 else 0
            total_intereses = 0
            costo_total = monto
        
        # Tabla de condiciones financieras - Solo campos que existen
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
        # TÉRMINOS DE LA OPERACIÓN DE CRÉDITO
        # ====================
        p.showPage()
        
        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(colors.HexColor('#1a365d'))
        p.drawCentredString(width/2, height - 50, "TÉRMINOS DE LA OPERACIÓN DE CRÉDITO")
        
        y = height - 100
        
        # Cuadro de términos - Solo campos que existen
        terminos = [
            ("Crédito Nº", numero_solicitud),
            ("Nombre del cliente", f"{persona.Nombres} {persona.Apellidos}"[:30]),
            ("Número identificación", f"{getattr(persona, 'TipoIdentificacion', 'ID')}: {persona.NumeroIdentificacion}"[:30]),
            ("Fecha desembolso", fecha_desembolso),
            ("Tasa E.A", f"{tasa_anual:.2f}%" if tasa_anual > 0 else "0.00%"),
            ("Tasa mora", "Máxima legal"),
            ("Período pago", "01 mensual"),
            ("Nº de Pagaré", numero_solicitud)
        ]
        
        # Dibujar tabla de términos
        for i, (label, value) in enumerate(terminos):
            # Fondo alternado
            if i % 2 == 0:
                p.setFillColor(colors.HexColor('#f7fafc'))
                p.rect(50, y - 15, width - 100, 25, fill=1, stroke=0)
            
            # Bordes
            p.setStrokeColor(colors.HexColor('#e2e8f0'))
            p.rect(50, y - 15, width - 100, 25)
            
            # Texto
            p.setFillColor(colors.black)
            p.setFont("Helvetica-Bold", 9)
            p.drawString(60, y - 10, label)
            p.setFont("Helvetica", 9)
            p.drawString(250, y - 10, str(value))
            
            y -= 25
        
        # ====================
        # TABLA DE AMORTIZACIÓN
        # ====================
        if amortizaciones:
            y -= 30
            p.setFont("Helvetica-Bold", 16)
            p.setFillColor(colors.HexColor('#1a365d'))
            p.drawCentredString(width/2, y, "TABLA DE AMORTIZACIÓN")
            y -= 40
            
            # Encabezados de la tabla
            headers = ["PERIODO", "FECHA", "CUOTA", "INTERÉS", "ABONO CAPITAL", "SALDO"]
            col_widths = [60, 90, 80, 80, 100, 100]
            col_positions = [50]
            
            for i in range(1, len(col_widths)):
                col_positions.append(col_positions[i-1] + col_widths[i-1])
            
            # Fondo para encabezados
            p.setFillColor(colors.HexColor('#2d3748'))
            p.rect(50, y - 20, width - 100, 25, fill=1, stroke=0)
            
            # Texto de encabezados
            p.setFont("Helvetica-Bold", 8)
            p.setFillColor(colors.white)
            for i, header in enumerate(headers):
                p.drawString(col_positions[i] + 5, y - 15, header)
            
            y -= 35
            
            # Datos de la tabla (primeros 25 periodos)
            p.setFont("Helvetica", 8)
            
            for i, amort in enumerate(amortizaciones[:25]):  # Mostrar primeros 25 periodos
                # Si nos quedamos sin espacio, nueva página
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
                
                # Fondo de fila
                p.rect(50, y - 15, width - 100, 20, fill=1, stroke=0)
                
                # Extraer valores de forma segura
                try:
                    if isinstance(amort, dict):
                        mes = amort.get('Mes', i + 1)
                        cuota = amort.get('Cuota', 0)
                        capital = amort.get('Capital', 0)
                        interes = amort.get('Interes', 0)
                        saldo = amort.get('CapitalVivo', 0)
                    else:
                        mes = amort.Mes if hasattr(amort, 'Mes') and amort.Mes else i + 1
                        cuota = amort.Cuota if hasattr(amort, 'Cuota') else 0
                        capital = amort.Capital if hasattr(amort, 'Capital') else 0
                        interes = amort.Interes if hasattr(amort, 'Interes') else 0
                        saldo = amort.CapitalVivo if hasattr(amort, 'CapitalVivo') else 0
                except:
                    mes = i + 1
                    cuota = capital = interes = saldo = 0
                
                # Calcular fecha aproximada usando la fecha actual
                fecha_actual = datetime.now()
                fecha_cuota = fecha_actual.replace(day=3)  # Siempre día 3 del mes
                
                # Texto de la fila
                p.setFillColor(colors.black)
                p.drawString(col_positions[0] + 5, y - 10, str(mes))
                p.drawString(col_positions[1] + 5, y - 10, fecha_cuota.strftime('%d/%m/%Y'))
                
                # Formatear valores monetarios
                try:
                    cuota_val = float(cuota) if cuota else 0
                    interes_val = float(interes) if interes else 0
                    capital_val = float(capital) if capital else 0
                    saldo_val = float(saldo) if saldo else 0
                    
                    p.drawString(col_positions[2] + 5, y - 10, f"${cuota_val:,.0f}")
                    p.drawString(col_positions[3] + 5, y - 10, f"${interes_val:,.0f}")
                    p.drawString(col_positions[4] + 5, y - 10, f"${capital_val:,.0f}")
                    p.drawString(col_positions[5] + 5, y - 10, f"${saldo_val:,.0f}")
                except:
                    p.drawString(col_positions[2] + 5, y - 10, "$0")
                    p.drawString(col_positions[3] + 5, y - 10, "$0")
                    p.drawString(col_positions[4] + 5, y - 10, "$0")
                    p.drawString(col_positions[5] + 5, y - 10, "$0")
                
                y -= 25
        else:
            # Si no hay amortizaciones
            y -= 30
            p.setFont("Helvetica-Bold", 14)
            p.setFillColor(colors.red)
            p.drawString(50, y, "NO HAY DATOS DE AMORTIZACIÓN DISPONIBLES")
            y -= 30
        
        # ====================
        # OBSERVACIONES FINALES
        # ====================
        p.showPage()
        
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(colors.HexColor('#1a365d'))
        p.drawString(50, height - 100, "OBSERVACIONES")
        
        y = height - 130
        
        observaciones = [
            "• El crédito se encuentra bajo un esquema de amortización decreciente de intereses.",
            "• La cuota mensual se mantiene constante durante el periodo mostrado.",
            "• Se recomienda verificar la tasa de interés nominal mensual con la entidad financiera.",
            "• Este documento es generado con fines informativos.",
            "• Valide toda la información con su oficina bancaria correspondiente.",
        ]
        
        p.setFont("Helvetica", 10)
        p.setFillColor(colors.black)
        for obs in observaciones:
            p.drawString(70, y, obs)
            y -= 20
        
        # Pie de página final
        y = 50
        p.setFont("Helvetica", 9)
        p.setFillColor(colors.HexColor('#6b7280'))
        p.drawCentredString(width/2, y, "Banco Financiero S.A. - Más banco. Más amigo.")
        p.setFont("Helvetica", 8)
        p.drawCentredString(width/2, y - 15, f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        p.drawCentredString(width/2, y - 30, "Documento informativo. Valide los datos con su oficina correspondiente.")
        
        # Guardar el PDF
        p.save()
        
        # Obtener el PDF del buffer
        buffer.seek(0)
        pdf = buffer.getvalue()
        buffer.close()
        
        # Crear respuesta HTTP
        response = HttpResponse(pdf, content_type='application/pdf')
        nombre_archivo = f"Informe_Credito_{persona.NumeroIdentificacion[:10]}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        
        return response
    
    def calcular_amortizacion(self, solicitud):
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
            
            return tabla
        except Exception as e:
            print(f"Error calculando amortización: {e}")
            return []