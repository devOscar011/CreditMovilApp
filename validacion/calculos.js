/**
 * Módulo de Cálculos Financieros - CreditApi
 * 
 * Implementa toda la lógica de cálculos financieros para el sistema de validación de créditos.
 * Incluye: cuotas, amortización, capacidad de pago y validación de solicitudes.
 * 
 * Usa Decimal para evitar problemas de precisión en números flotantes.
 */

const Decimal = require('decimal.js');

class CalculosFinancieros {
  // Constantes de negocio
  static TASA_INTERES_MINIMA = new Decimal("5.00");
  static TASA_INTERES_MAXIMA = new Decimal("35.00");
  static MONTO_MINIMO_PRESTAMO = new Decimal("5000.00");
  static MONTO_MAXIMO_PRESTAMO = new Decimal("500000.00");
  static PLAZO_MINIMO = 6;  // meses
  static PLAZO_MAXIMO = 120;  // meses
  static PORCENTAJE_INGRESOS_PERMITIDO = new Decimal("40.00");

  /**
   * Calcula la cuota mensual constante usando fórmula de amortización francesa.
   * 
   * Fórmula: Cuota = P × [r(1+r)^n] / [(1+r)^n - 1]
   * 
   * @param {number|Decimal} montoPrincipal - Monto del préstamo
   * @param {number|Decimal} tasaInteresAnual - Tasa de interés anual (%)
   * @param {number} plazoMeses - Plazo en meses
   * @returns {Decimal} Cuota mensual
   * @throws {Error} Si monto o plazo son inválidos
   */
  static calcularCuotaMensual(montoPrincipal, tasaInteresAnual, plazoMeses) {
    const P = new Decimal(montoPrincipal);
    const tasaAnual = new Decimal(tasaInteresAnual);
    const n = plazoMeses;

    if (P.lessThanOrEqualTo(0)) {
      throw new Error("El monto principal debe ser mayor a cero");
    }
    if (n <= 0) {
      throw new Error("El plazo debe ser mayor a cero");
    }

    const r = tasaAnual.dividedBy(100).dividedBy(12);  // Tasa mensual

    if (r.equals(0)) {
      return P.dividedBy(n).toDecimalPlaces(2);
    }

    const numerador = P.times(r).times((new Decimal(1).plus(r)).pow(n));
    const denominador = (new Decimal(1).plus(r)).pow(n).minus(1);
    
    return numerador.dividedBy(denominador).toDecimalPlaces(2);
  }

  /**
   * Calcula el interés mensual sobre el saldo de capital pendiente.
   * 
   * Fórmula: Interés = Saldo × (Tasa Anual / 12 / 100)
   * 
   * @param {number|Decimal} saldoCapital - Saldo de capital pendiente
   * @param {number|Decimal} tasaInteresAnual - Tasa de interés anual (%)
   * @returns {Decimal} Interés mensual
   */
  static calcularInteresMes(saldoCapital, tasaInteresAnual) {
    const saldo = new Decimal(saldoCapital);
    const tasaAnual = new Decimal(tasaInteresAnual);
    const tasaMensual = tasaAnual.dividedBy(100).dividedBy(12);
    
    return saldo.times(tasaMensual).toDecimalPlaces(2);
  }

  /**
   * Genera tabla completa de amortización mes a mes.
   * 
   * @param {number|Decimal} montoPrincipal - Monto del préstamo
   * @param {number|Decimal} tasaInteresAnual - Tasa de interés anual (%)
   * @param {number} plazoMeses - Plazo en meses
   * @param {Date} fechaInicio - Fecha de inicio del préstamo
   * @returns {Array<Object>} Tabla de amortización con estructura: {mes, cuota, capital, interes, saldoCapitalVivo}
   */
  static generarTablaAmortizacion(montoPrincipal, tasaInteresAnual, plazoMeses, fechaInicio = new Date()) {
    const P = new Decimal(montoPrincipal);
    const cuota = this.calcularCuotaMensual(P, tasaInteresAnual, plazoMeses);
    const tasaAnual = new Decimal(tasaInteresAnual);
    const r = tasaAnual.dividedBy(100).dividedBy(12);

    let saldo = new Decimal(P);
    const tabla = [];

    for (let mes = 1; mes <= plazoMeses; mes++) {
      const interes = saldo.times(r).toDecimalPlaces(2);
      const capital = cuota.minus(interes).toDecimalPlaces(2);
      saldo = saldo.minus(capital).toDecimalPlaces(2);

      tabla.push({
        mes: mes,
        cuota: cuota.toNumber(),
        capital: capital.toNumber(),
        interes: interes.toNumber(),
        saldoCapitalVivo: Math.max(saldo.toNumber(), 0)
      });
    }

    return tabla;
  }

  /**
   * Calcula la capacidad de pago de una persona.
   * 
   * Fórmula: 
   * - Flujo Caja Libre = Ingresos - Gastos - Deudas
   * - Cuota Máxima = Ingresos × 40%
   * 
   * @param {number|Decimal} ingresosMensuales - Ingresos mensuales
   * @param {number|Decimal} gastosMensuales - Gastos mensuales
   * @param {number|Decimal} deudasActuales - Deudas actuales
   * @returns {Object} {flujoLibre, cuotaMaximaPermitida, puedeAccederCredito}
   * @throws {Error} Si ingresos son cero
   */
  static calcularCapacidadPago(ingresosMensuales, gastosMensuales, deudasActuales) {
    const ingresos = new Decimal(ingresosMensuales);
    const gastos = new Decimal(gastosMensuales);
    const deudas = new Decimal(deudasActuales);

    if (ingresos.equals(0)) {
      throw new Error("Los ingresos no pueden ser cero");
    }

    const flujoLibre = ingresos.minus(gastos).minus(deudas).toDecimalPlaces(2);
    const cuotaMaxima = ingresos.times(this.PORCENTAJE_INGRESOS_PERMITIDO).dividedBy(100).toDecimalPlaces(2);

    return {
      flujoLibre: flujoLibre.toNumber(),
      cuotaMaximaPermitida: cuotaMaxima.toNumber(),
      puedeAccederCredito: flujoLibre.greaterThan(0)
    };
  }

  /**
   * Calcula el monto máximo de préstamo mediante búsqueda binaria.
   * 
   * Ajusta el monto para que la cuota mensual no exceda el 40% de ingresos.
   * 
   * @param {number|Decimal} ingresosMensuales - Ingresos mensuales
   * @param {number|Decimal} tasaInteresAnual - Tasa de interés anual (%)
   * @param {number} plazoMeses - Plazo en meses
   * @param {number|Decimal} gastosMensuales - Gastos mensuales
   * @param {number|Decimal} deudasActuales - Deudas actuales
   * @returns {Decimal} Monto máximo de préstamo
   */
  static calcularMontoMaximoPrestamo(ingresosMensuales, tasaInteresAnual, plazoMeses, gastosMensuales, deudasActuales) {
    const ingresos = new Decimal(ingresosMensuales);
    const capacidad = this.calcularCapacidadPago(ingresos, gastosMensuales, deudasActuales);
    const cuotaMaxima = new Decimal(capacidad.cuotaMaximaPermitida);

    let minMonto = this.MONTO_MINIMO_PRESTAMO;
    let maxMonto = this.MONTO_MAXIMO_PRESTAMO;
    let montoOptimo = this.MONTO_MINIMO_PRESTAMO;

    // Búsqueda binaria
    for (let i = 0; i < 50; i++) {
      const montoMedio = minMonto.plus(maxMonto).dividedBy(2).toDecimalPlaces(2);
      const cuotaPropuesta = this.calcularCuotaMensual(montoMedio, tasaInteresAnual, plazoMeses);

      if (cuotaPropuesta.lessThanOrEqualTo(cuotaMaxima)) {
        montoOptimo = montoMedio;
        minMonto = montoMedio;
      } else {
        maxMonto = montoMedio;
      }

      if (maxMonto.minus(minMonto).lessThanOrEqualTo(1)) {
        break;
      }
    }

    return montoOptimo;
  }

  /**
   * Valida una solicitud de crédito contra todos los requisitos de negocio.
   * 
   * Validaciones:
   * - Monto: RD$5,000 - RD$500,000
   * - Tasa: 5% - 35% anual
   * - Plazo: 6 - 120 meses
   * - Capacidad: Cuota ≤ 40% ingresos
   * - Solvencia: Ingresos > Gastos + Deudas
   * 
   * @param {number|Decimal} montoSolicitado - Monto solicitado
   * @param {number|Decimal} tasaInteres - Tasa de interés anual (%)
   * @param {number} plazoMeses - Plazo en meses
   * @param {number|Decimal} ingresosMensuales - Ingresos mensuales
   * @param {number|Decimal} gastosMensuales - Gastos mensuales
   * @param {number|Decimal} deudasActuales - Deudas actuales
   * @returns {Array} [esValida (boolean), mensaje (string)]
   */
  static validarSolicitudCredito(montoSolicitado, tasaInteres, plazoMeses, ingresosMensuales, gastosMensuales, deudasActuales) {
    const monto = new Decimal(montoSolicitado);
    const tasa = new Decimal(tasaInteres);
    const ingresos = new Decimal(ingresosMensuales);
    const gastos = new Decimal(gastosMensuales);
    const deudas = new Decimal(deudasActuales);

    // Validar monto
    if (monto.lessThan(this.MONTO_MINIMO_PRESTAMO)) {
      return [false, `El monto mínimo permitido es RD$${this.MONTO_MINIMO_PRESTAMO}`];
    }
    if (monto.greaterThan(this.MONTO_MAXIMO_PRESTAMO)) {
      return [false, `El monto máximo permitido es RD$${this.MONTO_MAXIMO_PRESTAMO}`];
    }

    // Validar tasa
    if (tasa.lessThan(this.TASA_INTERES_MINIMA) || tasa.greaterThan(this.TASA_INTERES_MAXIMA)) {
      return [false, `La tasa de interés debe estar entre ${this.TASA_INTERES_MINIMA}% y ${this.TASA_INTERES_MAXIMA}%`];
    }

    // Validar plazo
    if (plazoMeses < this.PLAZO_MINIMO || plazoMeses > this.PLAZO_MAXIMO) {
      return [false, `El plazo debe estar entre ${this.PLAZO_MINIMO} y ${this.PLAZO_MAXIMO} meses`];
    }

    // Validar solvencia básica
    const saldoPositivo = ingresos.minus(gastos).minus(deudas);
    if (saldoPositivo.lessThanOrEqualTo(0)) {
      return [false, `Ingresos insuficientes para cubrir gastos y deudas actuales`];
    }

    // Validar capacidad de pago
    const capacidad = this.calcularCapacidadPago(ingresos, gastos, deudas);
    const cuotaPropuesta = this.calcularCuotaMensual(monto, tasaInteres, plazoMeses);
    const cuotaMaximaPermitida = new Decimal(capacidad.cuotaMaximaPermitida);

    if (cuotaPropuesta.greaterThan(cuotaMaximaPermitida)) {
      return [false, `La cuota mensual (RD$${cuotaPropuesta}) excede la capacidad de pago (RD$${cuotaMaximaPermitida})`];
    }

    return [true, "Solicitud aprobada"];
  }
}

module.exports = CalculosFinancieros;
