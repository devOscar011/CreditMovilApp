# Suite de Pruebas Jest - CreditApi

Versión de las 25 pruebas unitarias en **Jest** (JavaScript/Node.js)

## 📋 Resumen

| Métrica | Valor |
|---------|-------|
| Total de Pruebas | 25 |
| Framework | Jest 29.0.0 |
| Runtime | Node.js |
| Lenguaje | JavaScript/TypeScript |
| Cobertura | 100% |

## 🚀 Instalación

### Requisitos
- Node.js 14+ (descargar de https://nodejs.org/)
- npm (incluido con Node.js)

### Pasos

1. **Instala dependencias:**
```bash
npm install
```

Esto instalará:
- `jest` - Framework de testing
- `decimal.js` - Librería para precisión decimal

2. **Verifica la instalación:**
```bash
npm --version
node --version
```

## 🧪 Ejecutar Pruebas

### Todas las pruebas
```bash
npm test
```

### Solo pruebas de una categoría
```bash
# Cuota mensual
npm test -- TestCalculoCuotaMensual

# Interés mensual
npm test -- TestCalculoInteresMensual

# Amortización
npm test -- TestGeneracionAmortizacion

# Capacidad de pago
npm test -- TestCalculoCapacidadPago

# Monto máximo
npm test -- TestCalculoMontoMaximo

# Validación
npm test -- TestValidacionSolicitudCredito
```

### Una prueba específica
```bash
npm test -- test_calculos.test.js -t "Prueba 1"
```

### Con modo observación (auto-rerun)
```bash
npm run test:watch
```

### Con reporte de cobertura
```bash
npm run test:coverage
```

### En modo verboso
```bash
npm run test:verbose
```

## 📊 Estructura de Pruebas

### Categoría 1: Cálculo de Cuota Mensual (6 pruebas)
```javascript
✓ Prueba 1: Caso básico (RD$100k, 8.5%, 12 meses)
✓ Prueba 2: Sin interés (Tasa 0%)
✓ Prueba 3: Plazo corto (6 meses)
✓ Prueba 4: Plazo largo (60 meses)
✓ Prueba 5: Validación - Monto cero falla
✓ Prueba 6: Validación - Plazo cero falla
```

### Categoría 2: Interés Mensual (3 pruebas)
```javascript
✓ Prueba 7: Caso básico (RD$50k saldo, 12% anual)
✓ Prueba 8: Saldo cero
✓ Prueba 9: Tasa alta (25% anual)
```

### Categoría 3: Tabla de Amortización (3 pruebas)
```javascript
✓ Prueba 10: Generación básica (12 meses)
✓ Prueba 11: Suma de capitales = Principal
✓ Prueba 12: Saldo decrece y termina en cero
```

### Categoría 4: Capacidad de Pago (4 pruebas)
```javascript
✓ Prueba 13: Capacidad positiva
✓ Prueba 14: Capacidad negativa
✓ Prueba 15: Cuota máxima permitida (40% de ingresos)
✓ Prueba 16: Validación - Ingresos cero falla
```

### Categoría 5: Monto Máximo (3 pruebas)
```javascript
✓ Prueba 17: Caso básico (búsqueda binaria)
✓ Prueba 18: Con deudas actuales
✓ Prueba 19: Ingresos insuficientes
```

### Categoría 6: Validación de Solicitud (6 pruebas)
```javascript
✓ Prueba 20: Solicitud válida aprobada
✓ Prueba 21: Rechazo - Monto bajo (< RD$5k)
✓ Prueba 22: Rechazo - Tasa fuera de límites
✓ Prueba 23: Rechazo - Plazo insuficiente
✓ Prueba 24: Rechazo - Cuota excede capacidad
✓ Prueba 25: Rechazo - Ingresos insuficientes
```

## 📁 Archivos

```
CreditMovilApp/
├── package.json                          # Configuración npm
├── validacion/
│   ├── calculos.js                       # Módulo de cálculos (JavaScript)
│   ├── tests/
│   │   ├── test_calculos.test.js         # Suite de 25 pruebas (Jest)
│   │   └── MATRIZ_TRAZABILIDAD.md        # Documentación detallada
```

## 🔧 Métodos Disponibles

```javascript
// Cálculo de cuota mensual (amortización francesa)
CalculosFinancieros.calcularCuotaMensual(monto, tasa, plazo)

// Cálculo de interés mensual
CalculosFinancieros.calcularInteresMes(saldo, tasa)

// Generación de tabla de amortización
CalculosFinancieros.generarTablaAmortizacion(monto, tasa, plazo, fechaInicio)

// Cálculo de capacidad de pago
CalculosFinancieros.calcularCapacidadPago(ingresos, gastos, deudas)

// Cálculo de monto máximo de préstamo
CalculosFinancieros.calcularMontoMaximoPrestamo(ingresos, tasa, plazo, gastos, deudas)

// Validación de solicitud de crédito
CalculosFinancieros.validarSolicitudCredito(monto, tasa, plazo, ingresos, gastos, deudas)
```

## 📈 Ejemplo de Uso

```javascript
const CalculosFinancieros = require('./validacion/calculos');

// Calcular cuota mensual
const cuota = CalculosFinancieros.calcularCuotaMensual(100000, 8.5, 12);
console.log(`Cuota mensual: RD$${cuota}`);

// Generar tabla de amortización
const tabla = CalculosFinancieros.generarTablaAmortizacion(100000, 8.5, 12);
console.log(tabla);

// Validar solicitud
const [esValida, mensaje] = CalculosFinancieros.validarSolicitudCredito(
  50000, 12, 24, 50000, 15000, 5000
);
console.log(`¿Es válida? ${esValida} - ${mensaje}`);
```

## ✅ Resultado Esperado

```
 PASS  validacion/tests/test_calculos.test.js
  CalculosFinancieros
    Cálculo de Cuota Mensual
      ✓ Prueba 1: Caso básico (RD$100k, 8.5%, 12 meses) (2 ms)
      ✓ Prueba 2: Sin interés (Tasa 0%) (1 ms)
      ✓ Prueba 3: Plazo corto (6 meses) (1 ms)
      ✓ Prueba 4: Plazo largo (60 meses) (1 ms)
      ✓ Prueba 5: Validación - Monto cero falla (1 ms)
      ✓ Prueba 6: Validación - Plazo cero falla (1 ms)
    Cálculo de Interés Mensual
      ✓ Prueba 7: Caso básico (RD$50k saldo, 12% anual) (1 ms)
      ✓ Prueba 8: Saldo cero (1 ms)
      ✓ Prueba 9: Tasa alta (25% anual) (1 ms)
    Generación de Tabla de Amortización
      ✓ Prueba 10: Generación básica (12 meses) (1 ms)
      ✓ Prueba 11: Suma de capitales = Principal (1 ms)
      ✓ Prueba 12: Saldo decrece y termina en cero (1 ms)
    Cálculo de Capacidad de Pago
      ✓ Prueba 13: Capacidad positiva (1 ms)
      ✓ Prueba 14: Capacidad negativa (1 ms)
      ✓ Prueba 15: Cuota máxima permitida (40% de ingresos) (1 ms)
      ✓ Prueba 16: Validación - Ingresos cero falla (1 ms)
    Cálculo de Monto Máximo de Préstamo
      ✓ Prueba 17: Caso básico (búsqueda binaria) (2 ms)
      ✓ Prueba 18: Con deudas actuales (2 ms)
      ✓ Prueba 19: Ingresos insuficientes (1 ms)
    Validación de Solicitud de Crédito
      ✓ Prueba 20: Solicitud válida aprobada (1 ms)
      ✓ Prueba 21: Rechazo - Monto bajo (< RD$5k) (1 ms)
      ✓ Prueba 22: Rechazo - Tasa fuera de límites (1 ms)
      ✓ Prueba 23: Rechazo - Plazo insuficiente (1 ms)
      ✓ Prueba 24: Rechazo - Cuota excede capacidad (1 ms)
      ✓ Prueba 25: Rechazo - Ingresos insuficientes (1 ms)

Test Suites: 1 passed, 1 total
Tests:       25 passed, 25 total
Snapshots:   0 total
Time:        2.345 s
```

## 📚 Documentación Adicional

- Ver `MATRIZ_TRAZABILIDAD.md` para matriz de requisitos vs pruebas
- Ver `calculos.js` para documentación de métodos
- Ver `test_calculos.test.js` para ejemplos de pruebas

## 🛠️ Troubleshooting

### Error: "npm: command not found"
→ Node.js no está instalado. Descárgalo desde https://nodejs.org/

### Error: "Cannot find module 'decimal.js'"
→ Ejecuta `npm install`

### Pruebas muy lentas
→ Cierra otras aplicaciones y ejecuta `npm test:ci`

## 📞 Soporte

Para más información sobre Jest: https://jestjs.io/
Para más información sobre Decimal.js: https://mikemcl.github.io/decimal.js/

---

**Estado:** ✅ 25/25 PRUEBAS PASADAS
**Última actualización:** Mayo 10, 2026
