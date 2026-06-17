"""
Módulo de Cálculos Financieros - CreditApi
============================================

Este módulo contiene todas las funciones de cálculo financiero utilizadas
en el sistema de validación de créditos. Incluye:

- Cálculo de cuotas mensuales
- Cálculo de interés simple y compuesto
- Generación de amortizaciones
- Análisis de capacidad de pago
- Validaciones de límites crediticios

Autor: CreditApi Team
Versión: 1.0
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class CalculosFinancieros:
    """
    Clase que encapsula toda la lógica de cálculos financieros del sistema.
    Utiliza Decimal para precisión en operaciones monetarias.
    """

    # Constantes del sistema
    TASA_INTERES_MINIMA = Decimal("5.00")  # 5% mínimo
    TASA_INTERES_MAXIMA = Decimal("35.00")  # 35% máximo
    MONTO_MINIMO_PRESTAMO = Decimal("5000.00")
    MONTO_MAXIMO_PRESTAMO = Decimal("500000.00")
    PLAZO_MINIMO = 6  # meses
    PLAZO_MAXIMO = 120  # meses
    PORCENTAJE_INGRESOS_PERMITIDO = Decimal("40.00")  # 40% de ingresos

    @staticmethod
    def calcular_cuota_mensual(
        monto_principal: Decimal,
        tasa_interes_anual: Decimal,
        plazo_meses: int
    ) -> Decimal:
        """
        Calcula la cuota mensual usando la fórmula de amortización francesa.

        Fórmula: C = P * [r(1+r)^n] / [(1+r)^n - 1]
        Donde:
        - P: Monto principal
        - r: Tasa de interés mensual
        - n: Número de períodos

        Args:
            monto_principal: Monto del préstamo en pesos
            tasa_interes_anual: Tasa de interés anual en porcentaje
            plazo_meses: Plazo en meses

        Returns:
            Decimal: Cuota mensual redondeada a 2 decimales

        Raises:
            ValueError: Si los parámetros están fuera de rangos válidos
        """
        if monto_principal <= 0:
            raise ValueError("El monto principal debe ser mayor a 0")
        if tasa_interes_anual < 0:
            raise ValueError("La tasa de interés no puede ser negativa")
        if plazo_meses < 1:
            raise ValueError("El plazo debe ser al menos 1 mes")

        # Convertir tasa anual a mensual (dividir entre 12)
        tasa_mensual = tasa_interes_anual / Decimal("100") / Decimal("12")

        # Si la tasa es 0, la cuota es simplemente el principal dividido entre meses
        if tasa_mensual == 0:
            cuota = monto_principal / Decimal(plazo_meses)
            return cuota.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Aplicar fórmula de amortización
        numerador = tasa_mensual * (1 + tasa_mensual) ** plazo_meses
        denominador = (1 + tasa_mensual) ** plazo_meses - 1
        cuota = monto_principal * (numerador / denominador)

        return cuota.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calcular_interes_mes(
        saldo_capital: Decimal,
        tasa_interes_anual: Decimal
    ) -> Decimal:
        """
        Calcula el interés correspondiente a un mes sobre el saldo de capital.

        Args:
            saldo_capital: Saldo pendiente de capital
            tasa_interes_anual: Tasa de interés anual en porcentaje

        Returns:
            Decimal: Interés del mes

        Raises:
            ValueError: Si los parámetros son inválidos
        """
        if saldo_capital < 0:
            raise ValueError("El saldo de capital no puede ser negativo")
        if tasa_interes_anual < 0:
            raise ValueError("La tasa de interés no puede ser negativa")

        tasa_mensual = (tasa_interes_anual / Decimal("100")) / Decimal("12")
        interes = saldo_capital * tasa_mensual

        return interes.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def generar_tabla_amortizacion(
        monto_principal: Decimal,
        tasa_interes_anual: Decimal,
        plazo_meses: int,
        fecha_inicio: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Genera la tabla de amortización completa del préstamo.

        Args:
            monto_principal: Monto del préstamo
            tasa_interes_anual: Tasa de interés anual
            plazo_meses: Plazo en meses
            fecha_inicio: Fecha de inicio (default: hoy)

        Returns:
            List[Dict]: Lista de cuotas con detalles mes a mes

        Raises:
            ValueError: Si los parámetros están fuera de rangos válidos
        """
        CalculosFinancieros._validar_parametros_prestamo(
            monto_principal, tasa_interes_anual, plazo_meses
        )

        if fecha_inicio is None:
            fecha_inicio = datetime.now()

        cuota_fija = CalculosFinancieros.calcular_cuota_mensual(
            monto_principal, tasa_interes_anual, plazo_meses
        )

        tabla = []
        saldo_vivo = monto_principal
        fecha_actual = fecha_inicio

        for mes in range(1, plazo_meses + 1):
            interes = CalculosFinancieros.calcular_interes_mes(
                saldo_vivo, tasa_interes_anual
            )
            capital = cuota_fija - interes
            saldo_vivo -= capital

            # Redondeo final para evitar valores negativos muy pequeños
            if saldo_vivo < Decimal("0.01"):
                saldo_vivo = Decimal("0.00")

            tabla.append({
                "mes": mes,
                "fecha": fecha_actual.strftime("%Y-%m-%d"),
                "cuota": float(cuota_fija),
                "capital": float(capital),
                "interes": float(interes),
                "saldo_vivo": float(saldo_vivo),
            })

            fecha_actual += timedelta(days=30)  # Aproximado

        return tabla

    @staticmethod
    def calcular_capacidad_pago(
        ingresos_mensuales: Decimal,
        gastos_mensuales: Decimal,
        deudas_actuales: Decimal
    ) -> Dict:
        """
        Calcula la capacidad de pago de un solicitante.

        Args:
            ingresos_mensuales: Ingresos mensuales netos
            gastos_mensuales: Gastos mensuales totales
            deudas_actuales: Deudas/obligaciones mensuales

        Returns:
            Dict: Información de capacidad de pago con ratios

        Raises:
            ValueError: Si los parámetros son inválidos
        """
        if ingresos_mensuales <= 0:
            raise ValueError("Los ingresos deben ser mayores a 0")
        if gastos_mensuales < 0:
            raise ValueError("Los gastos no pueden ser negativos")
        if deudas_actuales < 0:
            raise ValueError("Las deudas no pueden ser negativas")

        # Margen disponible
        margen_disponible = ingresos_mensuales - gastos_mensuales - deudas_actuales

        # Ratios de endeudamiento
        ratio_gastos = (gastos_mensuales / ingresos_mensuales * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        ratio_deudas = (deudas_actuales / ingresos_mensuales * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Cuota máxima permitida (40% de ingresos)
        cuota_maxima = (
            ingresos_mensuales * CalculosFinancieros.PORCENTAJE_INGRESOS_PERMITIDO / Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Capacidad real de pago
        capacidad_pago = (
            ingresos_mensuales - gastos_mensuales - deudas_actuales
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "ingresos_mensuales": float(ingresos_mensuales),
            "gastos_mensuales": float(gastos_mensuales),
            "deudas_actuales": float(deudas_actuales),
            "margen_disponible": float(margen_disponible),
            "ratio_gastos_porciento": float(ratio_gastos),
            "ratio_deudas_porciento": float(ratio_deudas),
            "cuota_maxima_permitida": float(cuota_maxima),
            "capacidad_pago_actual": float(capacidad_pago),
            "puede_endeudarse": capacidad_pago > 0,
        }

    @staticmethod
    def calcular_monto_maximo_prestamo(
        ingresos_mensuales: Decimal,
        tasa_interes_anual: Decimal,
        plazo_meses: int,
        gastos_mensuales: Decimal = Decimal("0"),
        deudas_actuales: Decimal = Decimal("0")
    ) -> Decimal:
        """
        Calcula el monto máximo de préstamo que puede acceder un solicitante
        basado en su capacidad de pago.

        Args:
            ingresos_mensuales: Ingresos mensuales del solicitante
            tasa_interes_anual: Tasa de interés ofrecida
            plazo_meses: Plazo en meses
            gastos_mensuales: Gastos mensuales (default: 0)
            deudas_actuales: Deudas actuales (default: 0)

        Returns:
            Decimal: Monto máximo de préstamo permitido

        Raises:
            ValueError: Si los parámetros son inválidos
        """
        # Capacidad disponible (40% de ingresos máximo)
        capacidad_maxima = (
            ingresos_mensuales * CalculosFinancieros.PORCENTAJE_INGRESOS_PERMITIDO / Decimal("100")
        ) - deudas_actuales - gastos_mensuales

        if capacidad_maxima <= 0:
            return Decimal("0")

        # Usar método iterativo para encontrar el monto (binary search)
        monto_bajo = CalculosFinancieros.MONTO_MINIMO_PRESTAMO
        monto_alto = CalculosFinancieros.MONTO_MAXIMO_PRESTAMO
        monto_optimo = monto_bajo

        while monto_bajo <= monto_alto:
            monto_medio = (monto_bajo + monto_alto) / Decimal("2")
            cuota = CalculosFinancieros.calcular_cuota_mensual(
                monto_medio, tasa_interes_anual, plazo_meses
            )

            if cuota <= capacidad_maxima:
                monto_optimo = monto_medio
                monto_bajo = monto_medio + Decimal("1")
            else:
                monto_alto = monto_medio - Decimal("1")

        return monto_optimo.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    @staticmethod
    def validar_solicitud_credito(
        monto_solicitado: Decimal,
        tasa_interes: Decimal,
        plazo_meses: int,
        ingresos_mensuales: Decimal,
        gastos_mensuales: Decimal,
        deudas_actuales: Decimal
    ) -> Tuple[bool, str]:
        """
        Valida una solicitud de crédito contra los criterios del sistema.

        Args:
            monto_solicitado: Monto solicitado
            tasa_interes: Tasa de interés anual
            plazo_meses: Plazo en meses
            ingresos_mensuales: Ingresos mensuales
            gastos_mensuales: Gastos mensuales
            deudas_actuales: Deudas actuales

        Returns:
            Tuple[bool, str]: (es_válida, mensaje_error)
        """
        # Validación de monto
        if monto_solicitado < CalculosFinancieros.MONTO_MINIMO_PRESTAMO:
            return (
                False,
                f"Monto mínimo permitido: {CalculosFinancieros.MONTO_MINIMO_PRESTAMO}"
            )
        if monto_solicitado > CalculosFinancieros.MONTO_MAXIMO_PRESTAMO:
            return (
                False,
                f"Monto máximo permitido: {CalculosFinancieros.MONTO_MAXIMO_PRESTAMO}"
            )

        # Validación de tasa de interés
        if tasa_interes < CalculosFinancieros.TASA_INTERES_MINIMA:
            return (False, "Tasa de interés por debajo del mínimo permitido")
        if tasa_interes > CalculosFinancieros.TASA_INTERES_MAXIMA:
            return (False, "Tasa de interés por encima del máximo permitido")

        # Validación de plazo
        if plazo_meses < CalculosFinancieros.PLAZO_MINIMO:
            return (False, f"Plazo mínimo: {CalculosFinancieros.PLAZO_MINIMO} meses")
        if plazo_meses > CalculosFinancieros.PLAZO_MAXIMO:
            return (False, f"Plazo máximo: {CalculosFinancieros.PLAZO_MAXIMO} meses")

        # Validación de capacidad de pago
        cuota_propuesta = CalculosFinancieros.calcular_cuota_mensual(
            monto_solicitado, tasa_interes, plazo_meses
        )
        capacidad = CalculosFinancieros.calcular_capacidad_pago(
            ingresos_mensuales, gastos_mensuales, deudas_actuales
        )

        if cuota_propuesta > Decimal(str(capacidad["cuota_maxima_permitida"])):
            return (False, "Cuota mensual excede capacidad de pago")

        return (True, "Solicitud válida")

    @staticmethod
    def _validar_parametros_prestamo(
        monto: Decimal,
        tasa: Decimal,
        plazo: int
    ) -> None:
        """
        Valida los parámetros básicos de un préstamo.

        Raises:
            ValueError: Si algún parámetro es inválido
        """
        if monto <= 0:
            raise ValueError("Monto debe ser mayor a 0")
        if tasa < 0:
            raise ValueError("Tasa de interés no puede ser negativa")
        if plazo < 1:
            raise ValueError("Plazo debe ser al menos 1 mes")
