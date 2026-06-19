from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from validacion.models import (
    Amortizacion,
    Conyuge,
    Domicilio,
    GastosMensuales,
    Laboral,
    Persona,
    ReferenciaPersonal,
    Solicitud,
)


def generar_tabla_amortizacion(monto, tasa_anual, plazo_meses):
    principal = Decimal(monto)
    tasa_mensual = (Decimal(tasa_anual) / Decimal("100")) / Decimal("12")
    plazo = int(plazo_meses)

    if plazo <= 0:
        raise ValueError("El plazo debe ser mayor que cero")

    if tasa_mensual == 0:
        cuota = (principal / plazo).quantize(Decimal("0.01"))
    else:
        factor = (Decimal("1") + tasa_mensual) ** plazo
        cuota = ((principal * tasa_mensual * factor) / (factor - Decimal("1"))).quantize(Decimal("0.01"))

    saldo = principal
    tabla = []
    for mes in range(1, plazo + 1):
        interes = (saldo * tasa_mensual).quantize(Decimal("0.01"))
        capital = (cuota - interes).quantize(Decimal("0.01"))
        saldo = (saldo - capital).quantize(Decimal("0.01"))
        if saldo < 0:
            saldo = Decimal("0.00")

        tabla.append(
            {
                "Mes": mes,
                "Cuota": cuota,
                "Capital": capital,
                "Interes": interes,
                "CapitalVivo": saldo,
            }
        )

    return tabla


class Command(BaseCommand):
    help = "Borra personas existentes opcionalmente y crea registros completos para analisis financiero."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Borra todas las personas existentes y sus datos relacionados antes de crear nuevos registros.",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=15,
            help="Cantidad de personas completas a crear. Por defecto: 15.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra lo que haria sin guardar cambios en la base de datos.",
        )

    def handle(self, *args, **options):
        count = options["count"]
        clear = options["clear"]
        dry_run = options["dry_run"]

        if count <= 0:
            raise CommandError("--count debe ser mayor que cero")

        try:
            with transaction.atomic():
                deleted = 0
                if clear:
                    deleted, _ = Persona.objects.all().delete()

                created_ids = []
                today = date.today()

                for index in range(1, count + 1):
                    persona = Persona.objects.create(
                        Nombres=f"Cliente{index:02d}",
                        Apellidos=f"Demo{index:02d}",
                        TipoIdentificacion="CEDULA",
                        NumeroIdentificacion=f"DEMO-FIN-{index:05d}",
                        Nacionalidad="Dominicana",
                        FechaNacimiento=date(1982 + (index % 18), ((index - 1) % 12) + 1, ((index - 1) % 27) + 1),
                        EstadoCivil="Casado",
                        Sexo="M" if index % 2 == 0 else "F",
                    )

                    ingresos = Decimal("28000.00") + (Decimal(index) * Decimal("1750.00"))
                    deudas = Decimal("2500.00") + (Decimal(index % 5) * Decimal("850.00"))
                    garantia = Decimal("160000.00") + (Decimal(index) * Decimal("12000.00"))

                    Laboral.objects.create(
                        IdPersona=persona,
                        TipoEmpleo="Contratado" if index % 3 else "Comerciante",
                        LugarTrabajo=f"Empresa Demo {index:02d}",
                        FechaContratacion=today - timedelta(days=365 * (3 + (index % 8))),
                        FechaAlCorriente=today,
                        IngresosMensuales=ingresos,
                        MontoGarantia=garantia,
                        MontoDeudas=deudas,
                    )

                    Domicilio.objects.create(
                        IdPersona=persona,
                        Direccion=f"Calle Financiera {index:02d}, Casa {100 + index}",
                        EstadoDomicilio="Propio" if index % 2 else "Alquilado",
                        MontoMensualidad=Decimal("4500.00") + (Decimal(index) * Decimal("250.00")),
                        Departamento="Santo Domingo",
                        Municipio="Distrito Nacional",
                        Barrio=f"Sector Demo {index:02d}",
                    )

                    Conyuge.objects.create(
                        IdPersona=persona,
                        NombreApellidos=f"Conyuge Demo {index:02d}",
                        NumeroCedula=f"CONY-FIN-{index:05d}",
                        NumeroPersonasACargo=1 + (index % 4),
                    )

                    GastosMensuales.objects.create(
                        IdPersona=persona,
                        Alimentacion=Decimal("6200.00") + (Decimal(index) * Decimal("140.00")),
                        VestimentaCalzado=Decimal("1500.00") + (Decimal(index) * Decimal("45.00")),
                        Transporte=Decimal("3200.00") + (Decimal(index) * Decimal("95.00")),
                        Colegiatura=Decimal("1800.00") if index % 3 == 0 else Decimal("0.00"),
                        OtrosGastos=Decimal("1200.00") + (Decimal(index) * Decimal("50.00")),
                        GastosSalud=Decimal("950.00") + (Decimal(index) * Decimal("35.00")),
                        Telecomunicaciones=Decimal("1100.00") + (Decimal(index) * Decimal("20.00")),
                        ServiciosAguaLuz=Decimal("2100.00") + (Decimal(index) * Decimal("60.00")),
                        ServiciosCableInternet=Decimal("1350.00") + (Decimal(index) * Decimal("25.00")),
                    )

                    for ref_index in range(1, 3):
                        ReferenciaPersonal.objects.create(
                            IdPersona=persona,
                            NombreApellido=f"Referencia {ref_index} Cliente {index:02d}",
                            NumeroContacto=f"809555{index:02d}{ref_index:02d}",
                        )

                    monto = Decimal("55000.00") + (Decimal(index) * Decimal("6500.00"))
                    plazo = 18 + ((index % 4) * 6)
                    tasa = Decimal("13.50") + (Decimal(index % 5) * Decimal("0.65"))

                    Solicitud.objects.create(
                        NumeroSolicitud=f"SOL-DEMO-FIN-{index:05d}",
                        TipoMoneda="DOP",
                        MontoSolicitado=monto,
                        PlazoFinanciero=plazo,
                        PropositoPrestamo="Capital de trabajo" if index % 2 else "Consumo",
                        TasaInteresAnual=tasa,
                        Estado="APROBADA" if index % 4 else "EN_REVISION",
                        IdPersona=persona,
                    )

                    for row in generar_tabla_amortizacion(monto, tasa, plazo):
                        Amortizacion.objects.create(IdPersona=persona, **row)

                    created_ids.append(persona.id)

                if dry_run:
                    raise RuntimeError("DRY_RUN_ROLLBACK")

        except RuntimeError as exc:
            if str(exc) != "DRY_RUN_ROLLBACK":
                raise
            self.stdout.write(self.style.WARNING("Dry run completado: no se guardaron cambios."))
            self.stdout.write(
                self.style.WARNING(
                    f"Se habrian borrado {deleted} objetos relacionados y creado {count} personas completas."
                )
            )
            return

        if clear:
            self.stdout.write(self.style.WARNING(f"Objetos borrados por cascada: {deleted}"))

        self.stdout.write(self.style.SUCCESS(f"Personas completas creadas: {count}"))
        self.stdout.write(self.style.SUCCESS(f"IDs creados: {', '.join(str(item) for item in created_ids)}"))
