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


CASOS_NICARAGUA = [
    {
        "nombres": "Carlos Alberto",
        "apellidos": "Mendoza Lopez",
        "cedula": "001-140284-1001A",
        "sexo": "M",
        "nacimiento": date(1984, 2, 14),
        "trabajo": "Distribuidora San Miguel",
        "direccion": "Reparto San Juan, casa 42",
        "departamento": "Managua",
        "municipio": "Managua",
        "barrio": "Reparto San Juan",
        "conyuge": "Maritza del Carmen Rivas",
        "referencias": ["Jorge Emilio Castillo", "Ana Patricia Duarte"],
        "proposito": "Capital de trabajo",
    },
    {
        "nombres": "Maria Fernanda",
        "apellidos": "Gutierrez Rocha",
        "cedula": "001-220790-1002B",
        "sexo": "F",
        "nacimiento": date(1990, 7, 22),
        "trabajo": "Clinica Santa Fe",
        "direccion": "Colonia Centroamerica, bloque 8",
        "departamento": "Managua",
        "municipio": "Managua",
        "barrio": "Colonia Centroamerica",
        "conyuge": "Luis Enrique Molina",
        "referencias": ["Karla Vanessa Silva", "Ramon Antonio Vega"],
        "proposito": "Mejoras de vivienda",
    },
    {
        "nombres": "Jose Antonio",
        "apellidos": "Perez Castillo",
        "cedula": "441-031185-1003C",
        "sexo": "M",
        "nacimiento": date(1985, 11, 3),
        "trabajo": "Agroservicios El Ganadero",
        "direccion": "Km 128 carretera a Matagalpa",
        "departamento": "Matagalpa",
        "municipio": "Matagalpa",
        "barrio": "Guanuca",
        "conyuge": "Rosa Argentina Mejia",
        "referencias": ["Miguel Angel Sequeira", "Silvia Elena Flores"],
        "proposito": "Compra de inventario",
    },
    {
        "nombres": "Sofia Carolina",
        "apellidos": "Ramirez Obando",
        "cedula": "281-180993-1004D",
        "sexo": "F",
        "nacimiento": date(1993, 9, 18),
        "trabajo": "Colegio San Ramon",
        "direccion": "Barrio Zaragoza, de la iglesia 2c al sur",
        "departamento": "Leon",
        "municipio": "Leon",
        "barrio": "Zaragoza",
        "conyuge": "Francisco Javier Arguello",
        "referencias": ["Helena Maria Ortega", "Oscar David Lacayo"],
        "proposito": "Consumo",
    },
    {
        "nombres": "Roberto Jose",
        "apellidos": "Chavarria Salinas",
        "cedula": "561-250681-1005E",
        "sexo": "M",
        "nacimiento": date(1981, 6, 25),
        "trabajo": "Taller Mecanico La Union",
        "direccion": "Barrio El Calvario, casa 19",
        "departamento": "Chinandega",
        "municipio": "Chinandega",
        "barrio": "El Calvario",
        "conyuge": "Claudia Maria Blandon",
        "referencias": ["Ernesto Javier Tellez", "Diana Mercedes Aguilar"],
        "proposito": "Compra de maquinaria",
    },
    {
        "nombres": "Gabriela del Socorro",
        "apellidos": "Morales Espinoza",
        "cedula": "041-120488-1006F",
        "sexo": "F",
        "nacimiento": date(1988, 4, 12),
        "trabajo": "Farmacia La Familiar",
        "direccion": "Barrio Monimbo, del parque 3c al este",
        "departamento": "Masaya",
        "municipio": "Masaya",
        "barrio": "Monimbo",
        "conyuge": "Julio Cesar Pineda",
        "referencias": ["Norma Isabel Ruiz", "Byron Alexander Prado"],
        "proposito": "Capital de trabajo",
    },
    {
        "nombres": "Eduardo Manuel",
        "apellidos": "Vargas Centeno",
        "cedula": "081-090286-1007G",
        "sexo": "M",
        "nacimiento": date(1986, 2, 9),
        "trabajo": "Cooperativa de Transporte Granada",
        "direccion": "Villa Sandino, lote 27",
        "departamento": "Granada",
        "municipio": "Granada",
        "barrio": "Villa Sandino",
        "conyuge": "Martha Lorena Espino",
        "referencias": ["German Antonio Solis", "Teresa Guadalupe Larios"],
        "proposito": "Reparacion de vehiculo",
    },
    {
        "nombres": "Ana Lucia",
        "apellidos": "Hernandez Mairena",
        "cedula": "121-300191-1008H",
        "sexo": "F",
        "nacimiento": date(1991, 1, 30),
        "trabajo": "Hotel Colonial Rivas",
        "direccion": "Barrio La Puebla, casa 15",
        "departamento": "Rivas",
        "municipio": "Rivas",
        "barrio": "La Puebla",
        "conyuge": "Kevin Mauricio Figueroa",
        "referencias": ["Elmer Jose Gutierrez", "Patricia del Carmen Corea"],
        "proposito": "Consumo",
    },
    {
        "nombres": "Juan Carlos",
        "apellidos": "Lopez Bermudez",
        "cedula": "161-171279-1009J",
        "sexo": "M",
        "nacimiento": date(1979, 12, 17),
        "trabajo": "Ferreteria El Progreso",
        "direccion": "Barrio Sandino, frente al mercado",
        "departamento": "Esteli",
        "municipio": "Esteli",
        "barrio": "Barrio Sandino",
        "conyuge": "Yadira del Rosario Cruz",
        "referencias": ["Manuel de Jesus Mendez", "Lucia Margarita Valdivia"],
        "proposito": "Compra de inventario",
    },
    {
        "nombres": "Veronica Isabel",
        "apellidos": "Navarro Zelaya",
        "cedula": "241-050594-1010K",
        "sexo": "F",
        "nacimiento": date(1994, 5, 5),
        "trabajo": "Panaderia La Segoviana",
        "direccion": "Barrio El Rosario, casa 33",
        "departamento": "Nueva Segovia",
        "municipio": "Ocotal",
        "barrio": "El Rosario",
        "conyuge": "Mario Antonio Duarte",
        "referencias": ["Carmen Elisa Palacios", "Nelson Alberto Baca"],
        "proposito": "Capital de trabajo",
    },
    {
        "nombres": "Miguel Angel",
        "apellidos": "Torres Urbina",
        "cedula": "321-270383-1011L",
        "sexo": "M",
        "nacimiento": date(1983, 3, 27),
        "trabajo": "Beneficio Cafetalero Jinotega",
        "direccion": "Comarca Las Lomas, casa comunal 1c norte",
        "departamento": "Jinotega",
        "municipio": "Jinotega",
        "barrio": "Las Lomas",
        "conyuge": "Sandra Patricia Mora",
        "referencias": ["Felipe Antonio Galeano", "Olga Marina Altamirano"],
        "proposito": "Compra de equipo agricola",
    },
    {
        "nombres": "Paola Andrea",
        "apellidos": "Alvarado Cardenas",
        "cedula": "201-101092-1012M",
        "sexo": "F",
        "nacimiento": date(1992, 10, 10),
        "trabajo": "Boutique Diriamba",
        "direccion": "Reparto Roberto Clemente, casa 8",
        "departamento": "Carazo",
        "municipio": "Diriamba",
        "barrio": "Roberto Clemente",
        "conyuge": "Cristian Daniel Padilla",
        "referencias": ["Luz Marina Guevara", "Edwin Rafael Baltodano"],
        "proposito": "Compra de inventario",
    },
    {
        "nombres": "Oscar Danilo",
        "apellidos": "Sanchez Reyes",
        "cedula": "361-230780-1013N",
        "sexo": "M",
        "nacimiento": date(1980, 7, 23),
        "trabajo": "Constructora Rio San Juan",
        "direccion": "Barrio 3 de Mayo, contiguo a la cancha",
        "departamento": "Rio San Juan",
        "municipio": "San Carlos",
        "barrio": "3 de Mayo",
        "conyuge": "Kenia Elizabeth Davila",
        "referencias": ["Hector Francisco Orozco", "Mayra Alejandra Rivas"],
        "proposito": "Mejoras de vivienda",
    },
    {
        "nombres": "Diana Mercedes",
        "apellidos": "Flores Molina",
        "cedula": "661-020689-1014P",
        "sexo": "F",
        "nacimiento": date(1989, 6, 2),
        "trabajo": "Comercial Bluefields",
        "direccion": "Barrio Punta Fria, casa 51",
        "departamento": "Costa Caribe Sur",
        "municipio": "Bluefields",
        "barrio": "Punta Fria",
        "conyuge": "Nelson Jose Hodgson",
        "referencias": ["Ruth Vanessa Taylor", "Henry Alexander Brooks"],
        "proposito": "Capital de trabajo",
    },
    {
        "nombres": "Luis Enrique",
        "apellidos": "Mejia Aguilar",
        "cedula": "461-150778-1015Q",
        "sexo": "M",
        "nacimiento": date(1978, 7, 15),
        "trabajo": "Ganaderia Los Robles",
        "direccion": "Comarca El Coyol, finca Los Robles",
        "departamento": "Boaco",
        "municipio": "Boaco",
        "barrio": "El Coyol",
        "conyuge": "Roxana del Carmen Somarriba",
        "referencias": ["Alvaro Jose Sequeira", "Miriam de los Angeles Lopez"],
        "proposito": "Compra de ganado",
    },
]


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
                    caso = CASOS_NICARAGUA[(index - 1) % len(CASOS_NICARAGUA)]
                    lote = ((index - 1) // len(CASOS_NICARAGUA)) + 1
                    numero_identificacion = caso["cedula"] if lote == 1 else f"{caso['cedula']}-{lote}"

                    persona = Persona.objects.create(
                        Nombres=caso["nombres"],
                        Apellidos=caso["apellidos"],
                        TipoIdentificacion="CEDULA",
                        NumeroIdentificacion=numero_identificacion,
                        Nacionalidad="Nicaraguense",
                        FechaNacimiento=caso["nacimiento"],
                        EstadoCivil="Casado",
                        Sexo=caso["sexo"],
                    )

                    ingresos = Decimal("18000.00") + (Decimal(index) * Decimal("1250.00"))
                    deudas = Decimal("1800.00") + (Decimal(index % 5) * Decimal("650.00"))
                    garantia = Decimal("85000.00") + (Decimal(index) * Decimal("9000.00"))

                    Laboral.objects.create(
                        IdPersona=persona,
                        TipoEmpleo="Contratado" if index % 3 else "Comerciante",
                        LugarTrabajo=caso["trabajo"],
                        FechaContratacion=today - timedelta(days=365 * (3 + (index % 8))),
                        FechaAlCorriente=today,
                        IngresosMensuales=ingresos,
                        MontoGarantia=garantia,
                        MontoDeudas=deudas,
                    )

                    Domicilio.objects.create(
                        IdPersona=persona,
                        Direccion=caso["direccion"],
                        EstadoDomicilio="Propio" if index % 2 else "Alquilado",
                        MontoMensualidad=Decimal("3500.00") + (Decimal(index) * Decimal("180.00")),
                        Departamento=caso["departamento"],
                        Municipio=caso["municipio"],
                        Barrio=caso["barrio"],
                    )

                    Conyuge.objects.create(
                        IdPersona=persona,
                        NombreApellidos=caso["conyuge"],
                        NumeroCedula=f"CONY-NI-{index:05d}",
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
                            NombreApellido=caso["referencias"][ref_index - 1],
                            NumeroContacto=f"5058{index:03d}{ref_index:04d}",
                        )

                    monto = Decimal("45000.00") + (Decimal(index) * Decimal("5000.00"))
                    plazo = 18 + ((index % 4) * 6)
                    tasa = Decimal("13.50") + (Decimal(index % 5) * Decimal("0.65"))

                    Solicitud.objects.create(
                        NumeroSolicitud=f"SOL-NI-{index:05d}",
                        TipoMoneda="NIO",
                        MontoSolicitado=monto,
                        PlazoFinanciero=plazo,
                        PropositoPrestamo=caso["proposito"],
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
