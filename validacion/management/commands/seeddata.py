from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from validacion.models import (
    Persona, Solicitud, Laboral, Domicilio, Conyuge,
    GastosMensuales, ReferenciaPersonal, Amortizacion,
)
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random


def generar_tabla_amortizacion(principal, tasa_anual, plazo_meses):
    P = Decimal(principal)
    r = (Decimal(tasa_anual) / Decimal(100)) / Decimal(12)
    n = int(plazo_meses)
    if r == 0:
        cuota = (P / n).quantize(Decimal('0.01'))
    else:
        numer = P * r * (1 + r) ** n
        denom = (1 + r) ** n - 1
        cuota = (numer / denom).quantize(Decimal('0.01'))

    saldo = P
    rows = []
    for mes in range(1, n + 1):
        interes = (saldo * r).quantize(Decimal('0.01'))
        capital = (cuota - interes).quantize(Decimal('0.01'))
        saldo = (saldo - capital).quantize(Decimal('0.01'))
        if saldo < 0:
            saldo = Decimal('0.00')
        rows.append({'mes': mes, 'cuota': cuota, 'capital': capital, 'interes': interes, 'saldo': saldo})
    return rows


class Command(BaseCommand):
    help = 'Seed the database with integrated test data for all validacion tables (idempotent)'

    def handle(self, *args, **options):
        # Create groups/roles
        roles = ['role_read', 'role_edit', 'role_admin']
        for r in roles:
            Group.objects.get_or_create(name=r)
        self.stdout.write(self.style.SUCCESS('Groups created/ensured'))

        # Create sample users and assign groups
        users = [
            ('user_reader', 'reader@example.com', 'ReaderPass123', ['role_read']),
            ('user_editor', 'editor@example.com', 'EditorPass123', ['role_edit']),
            ('user_manager', 'manager@example.com', 'ManagerPass123', ['role_edit', 'role_read']),
        ]
        for username, email, pwd, gs in users:
            u, created = User.objects.get_or_create(username=username, defaults={'email': email})
            if created:
                u.set_password(pwd)
                u.save()
            for g in gs:
                grp = Group.objects.get(name=g)
                u.groups.add(grp)
        self.stdout.write(self.style.SUCCESS('Sample users created/ensured'))

        # Create/ensure superuser admin with full permissions
        admin_username = 'admin'
        admin_email = 'admin@example.com'
        admin_password = 'AdminPass123!'
        admin, created = User.objects.get_or_create(username=admin_username, defaults={'email': admin_email})
        admin.is_staff = True
        admin.is_superuser = True
        admin.email = admin_email
        admin.set_password(admin_password)
        admin.save()
        self.stdout.write(self.style.SUCCESS(f'Admin user ensured: {admin_username}'))

        # Create 10 integrated Persona records and related objects
        personas = []
        today = date.today()
        for i in range(1, 11):
            tipo = 'DUI' if i % 2 == 0 else 'CEDULA'
            numero = f'{10000000 + i}' if tipo == 'CEDULA' else f'000{i:04d}-00{i%10}'
            nombres = f'Test{i}'
            apellidos = f'Persona{i}'
            nacimiento = date(1990 + (i % 10), (i % 12) + 1, (i % 26) + 1)
            nacionalidad = 'SV' if i % 2 == 0 else 'RD'
            estado_civil = 'Casado' if i % 3 == 0 else 'Soltero'
            sexo = 'M' if i % 2 == 0 else 'F'

            persona, created = Persona.objects.get_or_create(
                NumeroIdentificacion=numero,
                defaults={
                    'Nombres': nombres,
                    'Apellidos': apellidos,
                    'TipoIdentificacion': tipo,
                    'Nacionalidad': nacionalidad,
                    'FechaNacimiento': nacimiento,
                    'EstadoCivil': estado_civil,
                    'Sexo': sexo,
                }
            )

            # Laboral
            Laboral.objects.get_or_create(
                IdPersona=persona,
                defaults={
                    'TipoEmpleo': 'Contratado' if i % 2 == 0 else 'Comerciante',
                    'LugarTrabajo': f'Empresa{i}',
                    'FechaContratacion': nacimiento + timedelta(days=365*25),
                    'FechaAlCorriente': today,
                    'IngresosMensuales': Decimal('1500.00') + i * Decimal('100.00'),
                    'MontoGarantia': Decimal('0.00'),
                    'MontoDeudas': Decimal('100.00') * i,
                }
            )

            # Domicilio
            Domicilio.objects.get_or_create(
                IdPersona=persona,
                defaults={
                    'Direccion': f'Calle {i} # {i*10}',
                    'EstadoDomicilio': 'Propio' if i % 2 == 0 else 'Alquilado',
                    'MontoMensualidad': Decimal('300.00') + i * Decimal('10.00'),
                    'Departamento': 'DeptoX',
                    'Municipio': 'MunicipioY',
                    'Barrio': f'Barrio{i}',
                }
            )

            # Conyuge (only if Casado)
            if persona.EstadoCivil.lower().startswith('cas'):
                Conyuge.objects.get_or_create(
                    IdPersona=persona,
                    NombreApellidos=f'Conyuge{i}',
                    defaults={
                        'NumeroCedula': f'C{100000 + i}',
                        'NumeroPersonasACargo': i % 4,
                    }
                )

            # GastosMensuales
            GastosMensuales.objects.get_or_create(
                IdPersona=persona,
                defaults={
                    'Alimentacion': Decimal('200.00') + i * Decimal('5.00'),
                    'VestimentaCalzado': Decimal('50.00'),
                    'Transporte': Decimal('80.00'),
                    'Colegiatura': Decimal('0.00'),
                    'OtrosGastos': Decimal('20.00'),
                    'GastosSalud': Decimal('30.00'),
                    'Telecomunicaciones': Decimal('40.00'),
                    'ServiciosAguaLuz': Decimal('60.00'),
                    'ServiciosCableInternet': Decimal('30.00'),
                }
            )

            # ReferenciaPersonal (2 per persona)
            for r in range(1, 3):
                ReferenciaPersonal.objects.get_or_create(
                    IdPersona=persona,
                    NombreApellido=f'Ref{r}_Persona{i}',
                    defaults={'NumeroContacto': f'555-010{r}{i}'},
                )

            # Solicitud (one per persona)
            numero_solicitud = f'SOL-{persona.NumeroIdentificacion}-{i}'
            monto = Decimal('10000.00') + i * Decimal('500.00')
            plazo = 24
            tasa = Decimal('12.50')
            solicitud, s_created = Solicitud.objects.get_or_create(
                NumeroSolicitud=numero_solicitud,
                defaults={
                    'TipoMoneda': 'USD',
                    'MontoSolicitado': monto,
                    'PlazoFinanciero': plazo,
                    'PropositoPrestamo': 'Consumo',
                    'TasaInteresAnual': tasa,
                    'Estado': 'APROBADA',
                    'IdPersona': persona,
                }
            )

            # Amortizacion: create schedule for the persona based on the solicitud
            tabla = generar_tabla_amortizacion(monto, tasa, plazo)
            # clear existing amortizations for persona to avoid duplicates
            # (idempotent behavior)
            # Note: We won't delete, instead ensure by mes
            for row in tabla:
                Amortizacion.objects.update_or_create(
                    IdPersona=persona,
                    Mes=row['mes'],
                    defaults={
                        'Cuota': row['cuota'],
                        'Capital': row['capital'],
                        'Interes': row['interes'],
                        'CapitalVivo': row['saldo'],
                    }
                )

            personas.append(persona)

        self.stdout.write(self.style.SUCCESS(f'Created/ensured {len(personas)} Personas and related data'))
        self.stdout.write(self.style.SUCCESS('Integrated seeding complete.'))
