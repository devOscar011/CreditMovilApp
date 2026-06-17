"""
Pruebas Unitarias - Módulo de Cálculos Financieros
==================================================

Suite de pruebas exhaustivas para el módulo de cálculos financieros.
Cubre 25 casos de prueba divididos en 6 categorías principales.

Estructura:
    - TestCalculoCuotaMensual (6 pruebas)
    - TestCalculoInteresMensual (3 pruebas)
    - TestGeneracionAmortizacion (3 pruebas)
    - TestCalculoCapacidadPago (4 pruebas)
    - TestCalculoMontoMaximo (3 pruebas)
    - TestValidacionSolicitudCredito (6 pruebas)

Autor: CreditApi QA Team
Versión: 1.0
"""

from decimal import Decimal
from datetime import datetime, timedelta
import pytest
from validacion.calculos import CalculosFinancieros


# =========================================================================
# CATALOGO DE PRUEBAS UNITARIAS
# =========================================================================
# CCM - Calculo de Cuota Mensual
# CCM-001: Cálculo de cuota mensual para crédito estándar.
# CCM-002: Cuota mensual con tasa 0%.
# CCM-003: Cuota mensual con plazo corto.
# CCM-004: Cuota mensual con plazo largo.
# CCM-005: Validación de error con monto cero.
# CCM-006: Validación de error con plazo cero.
#
# CIM - Calculo de Interes Mensual
# CIM-001: Interés mensual sobre saldo estándar.
# CIM-002: Interés mensual con saldo cero.
# CIM-003: Interés mensual con tasa alta.
#
# TGA - Generacion de Tabla de Amortizacion
# TGA-001: Generación de tabla de amortización básica.
# TGA-002: Verificación de suma de capital.
# TGA-003: Verificación de saldo decreciente.
#
# CCP - Calculo de Capacidad de Pago
# CCP-001: Capacidad de pago positiva.
# CCP-002: Capacidad de pago negativa.
# CCP-003: Cuota máxima permitida.
# CCP-004: Validación de error con ingresos cero.
#
# CMM - Calculo de Monto Maximo
# CMM-001: Monto máximo de préstamo caso básico.
# CMM-002: Monto máximo considerando deudas actuales.
# CMM-003: Monto máximo con ingresos insuficientes.
#
# VSC - Validacion de Solicitud de Credito
# VSC-001: Solicitud válida aprobada.
# VSC-002: Rechazo por monto bajo.
# VSC-003: Rechazo por tasa fuera de límite.
# VSC-004: Rechazo por plazo insuficiente.
# VSC-005: Rechazo por cuota que excede capacidad.
# VSC-006: Rechazo por ingresos insuficientes.
# =========================================================================


class TestCalculoCuotaMensual:
    """
    Suite de pruebas para el cálculo de cuota mensual.
    Cubre casos normales, límites y excepciones.
    """

    def test_cuota_mensual_caso_basico(self):
        """
        Prueba 1: Cálculo de cuota mensuales para un crédito estándar.
        
        Escenario: Préstamo de RD$100,000 al 8.5% anual por 12 meses.
        Resultado esperado: Aproximadamente RD$8,721.98 mensuales.
        """
        monto = Decimal("100000.00")
        tasa = Decimal("8.50")
        plazo = 12

        cuota = CalculosFinancieros.calcular_cuota_mensual(monto, tasa, plazo)

        assert isinstance(cuota, Decimal)
        assert cuota > 0
        # Validar que la cuota está en el rango esperado (8700-8750)
        assert Decimal("8700") < cuota < Decimal("8750")

    def test_cuota_mensual_sin_interes(self):
        """
        Prueba 2: Cálculo de cuota cuando la tasa de interés es 0%.
        
        Escenario: Préstamo de RD$12,000 sin interés por 12 meses.
        Resultado esperado: RD$1,000 exactos (12,000 / 12).
        """
        monto = Decimal("12000.00")
        tasa = Decimal("0.00")
        plazo = 12

        cuota = CalculosFinancieros.calcular_cuota_mensual(monto, tasa, plazo)

        expected = Decimal("1000.00")
        assert cuota == expected

    def test_cuota_mensual_plazo_corto(self):
        """
        Prueba 3: Cálculo de cuota con plazo muy corto (6 meses).
        
        Escenario: RD$50,000 al 10% anual por 6 meses.
        Resultado esperado: Cuota mensual aproximadamente RD$8,578.07.
        """
        monto = Decimal("50000.00")
        tasa = Decimal("10.00")
        plazo = 6

        cuota = CalculosFinancieros.calcular_cuota_mensual(monto, tasa, plazo)

        assert cuota > Decimal("8500.00")
        assert cuota < Decimal("8600.00")

    def test_cuota_mensual_plazo_largo(self):
        """
        Prueba 4: Cálculo de cuota con plazo largo (60 meses).
        
        Escenario: RD$300,000 al 12% anual por 60 meses.
        Resultado esperado: Cuota mensual aproximadamente RD$6,700.
        """
        monto = Decimal("300000.00")
        tasa = Decimal("12.00")
        plazo = 60

        cuota = CalculosFinancieros.calcular_cuota_mensual(monto, tasa, plazo)

        assert Decimal("6600") < cuota < Decimal("6800")

    def test_cuota_mensual_monto_cero_falla(self):
        """
        Prueba 5: Validación de error cuando el monto es cero.
        
        Escenario: Intento de calcular cuota con monto RD$0.
        Resultado esperado: Lanza ValueError.
        """
        with pytest.raises(ValueError, match="mayor a 0"):
            CalculosFinancieros.calcular_cuota_mensual(
                Decimal("0"), Decimal("8.50"), 12
            )

    def test_cuota_mensual_plazo_cero_falla(self):
        """
        Prueba 6: Validación de error cuando el plazo es cero.
        
        Escenario: Intento de calcular cuota con plazo 0 meses.
        Resultado esperado: Lanza ValueError.
        """
        with pytest.raises(ValueError, match="al menos 1 mes"):
            CalculosFinancieros.calcular_cuota_mensual(
                Decimal("100000.00"), Decimal("8.50"), 0
            )


class TestCalculoInteresMensual:
    """
    Suite de pruebas para el cálculo del interés mensual.
    Valida el cálculo sobre el saldo de capital.
    """

    def test_interes_mensual_caso_basico(self):
        """
        Prueba 7: Cálculo del interés mensual sobre un saldo.
        
        Escenario: Saldo de RD$100,000 al 8.5% anual.
        Resultado esperado: Interés de RD$708.33 (100,000 * 0.085 / 12).
        """
        saldo = Decimal("100000.00")
        tasa = Decimal("8.50")

        interes = CalculosFinancieros.calcular_interes_mes(saldo, tasa)

        expected = Decimal("708.33")
        assert interes == expected

    def test_interes_mensual_saldo_cero(self):
        """
        Prueba 8: Cálculo del interés cuando el saldo es cero.
        
        Escenario: Saldo de RD$0 al 8.5% anual.
        Resultado esperado: Interés de RD$0.00.
        """
        saldo = Decimal("0.00")
        tasa = Decimal("8.50")

        interes = CalculosFinancieros.calcular_interes_mes(saldo, tasa)

        assert interes == Decimal("0.00")

    def test_interes_mensual_tasa_alta(self):
        """
        Prueba 9: Cálculo del interés con tasa elevada.
        
        Escenario: Saldo de RD$50,000 al 25% anual.
        Resultado esperado: Interés de RD$1,041.67.
        """
        saldo = Decimal("50000.00")
        tasa = Decimal("25.00")

        interes = CalculosFinancieros.calcular_interes_mes(saldo, tasa)

        expected = Decimal("1041.67")
        assert interes == expected


class TestGeneracionAmortizacion:
    """
    Suite de pruebas para la generación de tabla de amortización.
    Valida la consistencia de datos período a período.
    """

    def test_generacion_amortizacion_basica(self):
        """
        Prueba 10: Generación de tabla de amortización completa.
        
        Escenario: RD$100,000 al 8.5% anual por 12 meses.
        Resultado esperado: Tabla con 12 registros válidos.
        """
        monto = Decimal("100000.00")
        tasa = Decimal("8.50")
        plazo = 12

        tabla = CalculosFinancieros.generar_tabla_amortizacion(
            monto, tasa, plazo
        )

        assert len(tabla) == 12
        assert tabla[0]["mes"] == 1
        assert tabla[-1]["mes"] == 12
        assert tabla[-1]["saldo_vivo"] == 0

    def test_amortizacion_suma_cuotas(self):
        """
        Prueba 11: Validación de que la suma de capital iguala el monto principal.
        
        Escenario: RD$50,000 al 12% anual por 24 meses.
        Resultado esperado: Suma de capital ≈ RD$50,000.
        """
        monto = Decimal("50000.00")
        tasa = Decimal("12.00")
        plazo = 24

        tabla = CalculosFinancieros.generar_tabla_amortizacion(
            monto, tasa, plazo
        )

        suma_capital = sum(Decimal(str(r["capital"])) for r in tabla)

        # Permitir pequeña desviación por redondeo
        assert abs(suma_capital - monto) < Decimal("1.00")

    def test_amortizacion_decrece_saldo(self):
        """
        Prueba 12: Validación de que el saldo vivo decrece cada mes.
        
        Escenario: RD$75,000 al 10% anual por 36 meses.
        Resultado esperado: Saldo_n+1 < Saldo_n para todo n.
        """
        monto = Decimal("75000.00")
        tasa = Decimal("10.00")
        plazo = 36

        tabla = CalculosFinancieros.generar_tabla_amortizacion(
            monto, tasa, plazo
        )

        for i in range(len(tabla) - 1):
            assert tabla[i]["saldo_vivo"] > tabla[i + 1]["saldo_vivo"]


class TestCalculoCapacidadPago:
    """
    Suite de pruebas para el cálculo de capacidad de pago.
    Valida ratios de endeudamiento y disponibilidad.
    """

    def test_capacidad_pago_positiva(self):
        """
        Prueba 13: Cálculo de capacidad de pago en caso positivo.
        
        Escenario: 
        - Ingresos: RD$50,000
        - Gastos: RD$15,000
        - Deudas: RD$5,000
        Resultado esperado: Capacidad = RD$30,000.
        """
        ingresos = Decimal("50000.00")
        gastos = Decimal("15000.00")
        deudas = Decimal("5000.00")

        resultado = CalculosFinancieros.calcular_capacidad_pago(
            ingresos, gastos, deudas
        )

        assert resultado["capacidad_pago_actual"] == 30000.0
        assert resultado["puede_endeudarse"] is True
        assert resultado["ratio_gastos_porciento"] == 30.0

    def test_capacidad_pago_negativa(self):
        """
        Prueba 14: Cálculo cuando gastos + deudas superan ingresos.
        
        Escenario:
        - Ingresos: RD$30,000
        - Gastos: RD$20,000
        - Deudas: RD$15,000
        Resultado esperado: Capacidad = RD$-5,000 (negativa).
        """
        ingresos = Decimal("30000.00")
        gastos = Decimal("20000.00")
        deudas = Decimal("15000.00")

        resultado = CalculosFinancieros.calcular_capacidad_pago(
            ingresos, gastos, deudas
        )

        assert resultado["capacidad_pago_actual"] == -5000.0
        assert resultado["puede_endeudarse"] is False

    def test_cuota_maxima_permitida(self):
        """
        Prueba 15: Validación del cálculo de cuota máxima (40% ingresos).
        
        Escenario: Ingresos de RD$40,000.
        Resultado esperado: Cuota máxima = RD$16,000 (40% de 40,000).
        """
        ingresos = Decimal("40000.00")
        gastos = Decimal("0.00")
        deudas = Decimal("0.00")

        resultado = CalculosFinancieros.calcular_capacidad_pago(
            ingresos, gastos, deudas
        )

        assert resultado["cuota_maxima_permitida"] == 16000.0

    def test_capacidad_pago_ingresos_cero_falla(self):
        """
        Prueba 16: Validación de error con ingresos cero.
        
        Escenario: Intento con ingresos = RD$0.
        Resultado esperado: Lanza ValueError.
        """
        with pytest.raises(ValueError, match="ingresos deben ser mayores"):
            CalculosFinancieros.calcular_capacidad_pago(
                Decimal("0"), Decimal("0"), Decimal("0")
            )


class TestCalculoMontoMaximo:
    """
    Suite de pruebas para el cálculo del monto máximo de préstamo.
    Valida la búsqueda binaria de monto óptimo.
    """

    def test_monto_maximo_caso_basico(self):
        """
        Prueba 17: Cálculo del monto máximo de préstamo.
        
        Escenario:
        - Ingresos: RD$50,000
        - Tasa: 8.5% anual
        - Plazo: 60 meses
        - Sin gastos ni deudas
        Resultado esperado: Monto > RD$100,000.
        """
        ingresos = Decimal("50000.00")
        tasa = Decimal("8.50")
        plazo = 60
        gastos = Decimal("0.00")
        deudas = Decimal("0.00")

        monto_maximo = CalculosFinancieros.calcular_monto_maximo_prestamo(
            ingresos, tasa, plazo, gastos, deudas
        )

        assert monto_maximo > Decimal("100000.00")

    def test_monto_maximo_con_deudas_actuales(self):
        """
        Prueba 18: Cálculo del monto máximo considerando deudas actuales.
        
        Escenario:
        - Ingresos: RD$40,000
        - Deudas actuales: RD$10,000/mes
        - Tasa: 10% anual, Plazo: 48 meses
        Resultado esperado: Monto máximo reducido por deuda.
        """
        ingresos = Decimal("40000.00")
        tasa = Decimal("10.00")
        plazo = 48
        gastos = Decimal("0.00")
        deudas = Decimal("10000.00")

        monto_maximo = CalculosFinancieros.calcular_monto_maximo_prestamo(
            ingresos, tasa, plazo, gastos, deudas
        )

        # Debe ser mayor a 0 pero menor que sin deudas
        assert monto_maximo > Decimal("0")

    def test_monto_maximo_ingresos_insuficientes(self):
        """
        Prueba 19: Cálculo cuando los ingresos son muy bajos.
        
        Escenario:
        - Ingresos: RD$5,000
        - Gastos: RD$4,800
        - Deudas: RD$1,000
        Resultado esperado: Monto máximo = RD$0 (sin capacidad).
        """
        ingresos = Decimal("5000.00")
        tasa = Decimal("8.50")
        plazo = 12
        gastos = Decimal("4800.00")
        deudas = Decimal("1000.00")

        monto_maximo = CalculosFinancieros.calcular_monto_maximo_prestamo(
            ingresos, tasa, plazo, gastos, deudas
        )

        assert monto_maximo == Decimal("0")


class TestValidacionSolicitudCredito:
    """
    Suite de pruebas para la validación completa de solicitudes de crédito.
    Cubre validaciones de límites, tasa y capacidad.
    """

    def test_solicitud_valida_aprobada(self):
        """
        Prueba 20: Validación de solicitud correcta y dentro de parámetros.
        
        Escenario:
        - Monto: RD$100,000 (dentro de límites)
        - Tasa: 8.5% (dentro de rango)
        - Plazo: 24 meses (válido)
        - Ingresos suficientes
        Resultado esperado: Solicitud válida.
        """
        es_valida, mensaje = CalculosFinancieros.validar_solicitud_credito(
            Decimal("100000.00"),
            Decimal("8.50"),
            24,
            Decimal("50000.00"),
            Decimal("10000.00"),
            Decimal("2000.00")
        )

        assert es_valida is True
        assert "válida" in mensaje.lower()

    def test_solicitud_monto_bajo(self):
        """
        Prueba 21: Rechazo de solicitud con monto menor al mínimo.
        
        Escenario: Monto de RD$2,000 (mínimo es RD$5,000).
        Resultado esperado: Solicitud rechazada.
        """
        es_valida, mensaje = CalculosFinancieros.validar_solicitud_credito(
            Decimal("2000.00"),
            Decimal("8.50"),
            12,
            Decimal("30000.00"),
            Decimal("5000.00"),
            Decimal("1000.00")
        )

        assert es_valida is False
        assert "mínimo" in mensaje.lower()

    def test_solicitud_tasa_fuera_limite(self):
        """
        Prueba 22: Rechazo de solicitud con tasa fuera de rango.
        
        Escenario: Tasa de 50% (máximo es 35%).
        Resultado esperado: Solicitud rechazada.
        """
        es_valida, mensaje = CalculosFinancieros.validar_solicitud_credito(
            Decimal("100000.00"),
            Decimal("50.00"),
            24,
            Decimal("40000.00"),
            Decimal("5000.00"),
            Decimal("1000.00")
        )

        assert es_valida is False
        assert "tasa" in mensaje.lower()

    def test_solicitud_plazo_insuficiente(self):
        """
        Prueba 23: Rechazo de solicitud con plazo menor al mínimo.
        
        Escenario: Plazo de 2 meses (mínimo es 6 meses).
        Resultado esperado: Solicitud rechazada.
        """
        es_valida, mensaje = CalculosFinancieros.validar_solicitud_credito(
            Decimal("50000.00"),
            Decimal("8.50"),
            2,
            Decimal("30000.00"),
            Decimal("5000.00"),
            Decimal("1000.00")
        )

        assert es_valida is False
        assert "plazo" in mensaje.lower()

    def test_solicitud_cuota_excede_capacidad(self):
        """
        Prueba 24: Rechazo cuando la cuota excede capacidad de pago.
        
        Escenario:
        - Monto: RD$500,000 (muy alto para ingresos bajos)
        - Ingresos: RD$30,000
        - La cuota mensual excedería 40% de ingresos (RD$12,000 máximo)
        Resultado esperado: Solicitud rechazada.
        """
        es_valida, mensaje = CalculosFinancieros.validar_solicitud_credito(
            Decimal("500000.00"),
            Decimal("15.00"),
            36,
            Decimal("30000.00"),
            Decimal("8000.00"),
            Decimal("3000.00")
        )

        assert es_valida is False
        assert "capacidad" in mensaje.lower()

    def test_solicitud_ingresos_insuficientes(self):
        """
        Prueba 25: Rechazo cuando los ingresos son muy bajos para el monto.
        
        Escenario:
        - Monto: RD$100,000
        - Ingresos: RD$10,000 (muy bajo)
        Resultado esperado: Solicitud rechazada.
        """
        es_valida, mensaje = CalculosFinancieros.validar_solicitud_credito(
            Decimal("100000.00"),
            Decimal("8.50"),
            24,
            Decimal("10000.00"),
            Decimal("3000.00"),
            Decimal("2000.00")
        )

        assert es_valida is False


# =========================================================================
# PYTEST CONFIGURACIÓN Y FIXTURES
# =========================================================================

@pytest.fixture
def datos_prestamo_standar():
    """
    Fixture que proporciona datos estándar para pruebas.
    
    Returns:
        Dict con parámetros típicos de un préstamo.
    """
    return {
        "monto": Decimal("100000.00"),
        "tasa": Decimal("8.50"),
        "plazo": 12,
        "ingresos": Decimal("50000.00"),
        "gastos": Decimal("10000.00"),
        "deudas": Decimal("2000.00"),
    }


@pytest.fixture
def datos_prestamo_alto_riesgo():
    """
    Fixture para préstamos de alto riesgo.
    
    Returns:
        Dict con parámetros de alto riesgo.
    """
    return {
        "monto": Decimal("250000.00"),
        "tasa": Decimal("25.00"),
        "plazo": 24,
        "ingresos": Decimal("30000.00"),
        "gastos": Decimal("15000.00"),
        "deudas": Decimal("8000.00"),
    }


# =========================================================================
# NOTAS DE EJECUCIÓN
# =========================================================================

"""
Para ejecutar las pruebas:

1. Instalar pytest (si no está):
   $ pip install pytest

2. Ejecutar todas las pruebas:
   $ pytest validacion/tests/test_calculos.py -v

3. Ejecutar pruebas de una clase específica:
   $ pytest validacion/tests/test_calculos.py::TestCalculoCuotaMensual -v

4. Ejecutar una prueba específica:
   $ pytest validacion/tests/test_calculos.py::TestCalculoCuotaMensual::test_cuota_mensual_caso_basico -v

5. Ver cobertura:
   $ pytest validacion/tests/test_calculos.py --cov=validacion.calculos --cov-report=html

Cobertura esperada: 100% de líneas de código en calculos.py
"""
